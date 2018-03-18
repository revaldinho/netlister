package vnx;
/**
 *
 * @version $Id: parser.java,v 1.1 2006/03/06 21:09:05 richarde Exp $
 *
 * Basic parser class for use with test vector processing utilities.
 * 
 */
import java.io.*;

public class parser {
    public StreamTokenizer st;
    public String token;
    public boolean debugMode = false;  
    
    public parser( BufferedReader inStream) {
        super();
        st = new StreamTokenizer( new BufferedReader(inStream)); 
        SetupSyntax();
    }
    
    public parser( File file) throws IOException{
        super();
        FileReader fileIn = new FileReader(file);
        st = new StreamTokenizer(new BufferedReader(fileIn));
        SetupSyntax();
    }

    public parser( String fileName) throws IOException{
        FileReader fileIn = new FileReader(fileName);
        st = new StreamTokenizer(new BufferedReader(fileIn));
        SetupSyntax();
    }

    /** Add a character to be interpreted as a normal word character */ 
    public void addWordChar(char c) {
        st.wordChars(c,c);
    }

    /**
     * Get the next token from the input data stream. 
     *
     * Returns true if passed over end of line to get the current token
     */

    public boolean advance() {
        boolean passedEOL = false;
        try {
            if ( st.nextToken() != StreamTokenizer.TT_EOF) {
                if ( st.ttype == StreamTokenizer.TT_WORD ) {
                    if (debugMode)
                        System.out.println("LN "+st.lineno()+" String: "+st.sval);
                    token = st.sval; 
                } else if ( st.ttype == StreamTokenizer.TT_NUMBER ) {
                    if (debugMode)
                        System.out.println("LN "+st.lineno()+" Number: "+st.nval);
                    token = new String( Double.toString(st.nval) );
                } else if ( st.ttype == StreamTokenizer.TT_EOL ) {
                    passedEOL = true;
                    advance();	// no use for eol tokens, so move on
                } else {
                    // must be an 'ordinary' character; return it as a string
                    char c = (char)st.ttype;
                    if (debugMode)
                        System.out.println("LN "+st.lineno()+" ordinary char: "+ c) ;
                    token = new String( ""+c );
                }
            } else {
                token = "(eof)";
            }
        } catch ( IOException e) {
            error( "IOException occurred during token fetching:\n"+e.toString());
        }
        return passedEOL;
    }

    /**
     * If the current token is not equal to the given string then print an error,
     * otherwise consume the token and advance, returning 'true' if we passed
     * over an end-of-line marker to fetch the next token.
     */

    public boolean eat(String s) {
        if ( ! s.equalsIgnoreCase(token) ) {
            error ( "Saw token "+token+", expecting "+s );
        }
        return ( advance()) ;
    }
    
    public void error(String s) {
        System.out.println( "Error on line number "+st.lineno() +"\n"+s );
        System.exit(1);
    }
    
    
    public void SetupSyntax() {
        //
        // NB numbers appear in words so long as the word begins
        // with an alphabetic character.
        //
        st.resetSyntax();
        st.whitespaceChars(0, ' ');  
        st.wordChars('a','z');
        st.wordChars('A','Z');
        st.wordChars('_','_');
        //st.wordChars('-','-');
        //st.wordChars('+','+');
        //st.wordChars('.','.');
        //st.wordChars('[',']');
        st.wordChars('0','9');
        st.quoteChar('"');
        st.quoteChar('\'');
        st.eolIsSignificant( true );
        st.slashSlashComments( true ); // enable "//" comment lines
        st.lowerCaseMode( false) ;      // Convert all words to lower case if set 
    }
    
    
    /** Treat the current token as a string, returning its value and
     * advancing to the next token. This routine is a placeholder
     * to allow 'identifiers' to be more complex than the parser
     * currently allows. eg we could allow punctuation, numbers etc
     * in an identifier name, so this routine would concatenate all
     * valid tokens until an invalid one were reached.
     */
    public String getIdent() {
        String s = token;
        advance();
        return s;
    }
    
    public double getDouble() {
        // Convert the current token into a double, handling
        // the number format exception if necessary. If successful
        // advance to the next token and return the double value.
        double num = 0;
        try {
            num = new Double(token).doubleValue();
        } catch (NumberFormatException e) {
            error("Bad number format: found "+token+" when expecting double precision number");
        }
        advance();
        return num;
    }
    
    public long getLong() {
        // Convert the current token into a long integer, handling
        // the number format exception if necessary. If successful
        // advance to the next token and return the long value.
        long num = 0;
        try {
            num = Long.parseLong( token );
        } catch (NumberFormatException e) {
            error("Bad number format: found "+token+" when expecting long integer number");
        }
        advance();
        return num;
    }
    
  public void readToEndOfClause( String startMarker, String endMarker ) {
      //
      // Read all data up to and including the end of clause marker. If
      // another clause is started, then recursively read through that too.
      // Eats the final endMarker token before returning, pointing to the
      // next token for processing.
      //
      while (! ( token.equalsIgnoreCase( "(eof)")) ){
          if ( token.equals(endMarker)) {
              // End of clause so eat the token and return
              eat(endMarker);
              return;
          } else if ( token.equals(startMarker)){
              // Start of another clause, so eat it all and return
              eat(startMarker);
              readToEndOfClause(startMarker, endMarker);
          } else {
              // Otherwise just munch up the data and advance
              advance();
          }
      }
      if ( token.equalsIgnoreCase( "(eof)") ) {
          error( "Unexpected End of File found (unbalanced opening and closing "+startMarker+" and "+endMarker+ " )");
      }
  }
    
}

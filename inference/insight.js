// Initial Setups
const filesys = require("fs");
const PersonalityInsightsV3 = require('watson-developer-cloud/personality-insights/v3');
const insight = new PersonalityInsightsV3({ version: '2020-01-16' });
const summary = require('personality-text-summary');
const engSummary = new summary({
  locale: 'en',
  version: 'v3'
});
require("dotenv").config();

// Parse the data from IBM Watsons' API.
filesys.readFile('test-case.txt', function(err, data) {
  if(err) {
    return console.log(err);
  }

  insight
  .profile({
    content: data.toString(),
    content_type: "text/plain",
    consumption_preferences: true,
    raw_scores: true
  })
  .then(result => {
    console.log(JSON.stringify(result, null, 2));
    console.log("\n\n\nSummary of the personality: ");
    console.log(getSummary(result));
  })
  .catch(err => {
    console.log("error:", err);
  });
});

// Summarize all the data.
const getSummary = personalityProfile => {
  let textSummary = engSummary.getSummary(personalityProfile);
  if(typeof(textSummary) !== 'string') {
    console.log("Error getting summary!");
  }
  else {
    return textSummary;
  }
};

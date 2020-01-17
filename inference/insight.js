/* TODO
  - Use text files for test-cases.
*/

// Initial Setup
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
  console.log("Data: " + data.toString());
})

insight
  .profile({
    content: "Gudang Garam celebrated its 60th anniversary in 2018, and it is especially pleasing that it was a year of achievement, with new records in sales revenue and in the volume of products shipped. Despite strong competition, we gained market share and delivered sound earnings performance. Sales revenue grew 14.9 per cent to Rp 95.7 trillion, with profit for the year of Rp 7.8 trillion or Rp 4,050 earnings per share. A dividend of Rp 2,600 per share was approved and distributed to shareholders. Throughout 2018 Gudang Garam has demonstrated that the combination of high standards in product quality, ease of availability and effective pricing has been rewarded by solid growth and brand loyalty. Operating conditions for the business community have been challenging. While some recovery is evident in commodities, domestic consumption remains the key driver in the economy. A mixed picture emerged in consumer spending in 2018 impacted by a number of different factors, expansion in the digital economy has created new jobs but with a trade-off as part time casual labour is on the rise versus fixed salaries and job security. Continuing the trend of past years national demand for tobacco products eased among a downturn across all major consumer categories, with another lacklustre year for retailing and prices in general reflecting the weakening of the Rupiah. Reduced buying power and to a degree, changing consumer attitudes to smoking were evident, and while we continue to monitor these developments, we are staying focused on strong fundamentals. Indonesia today is the world’s seventh largest economy based on purchasing power parity and remains on course to become one of the top ten economies within a decade. Despite lower spending, economic growth in 2018 was sustained, at a rate of 5.2 per cent, slightly higher than the previous year, with inflation lower than expected and a prudent fiscal policy earning Indonesia a reputation for stability as the ‘resilience economy’. Successful hosting of the Asian Games, the Para Games and the IMF-World Bank meeting helped raise Indonesia’s international profile. Externally, the USA-China trade tensions,disruption in the Gulf and a lack of resolution in UK’s planned exit from Europe impacted the world economic outlook. This resulted in some pressure on the emerging economy currencies, including the Rupiah, however Gudang Garam was not materially affected, with little exposure to exchange movements. Success in any consumer market is hard won and tough to maintain. Contraction of the cigarette market in recent years has not diminished its appeal, with competition more intense than ever. Inevitably as the range of choice expands, prices come under pressure, while input costs still rise and this has squeezed profitability. Excise rates were again raised in 2018. The decision not to raise excise for 2019 offers some respite, a chance to rebuild profitability, but the strong shift into lower ‘value’ priced brands is unlikely to change in the short term. The full flavour, machine made category in which Gudang Garam has a strong following, continued to gain market share, while demand for hand rolled products fell. There were no additional restrictions imposed on advertising,promotions or packaging and we concentrated on maintaining the appeal of our established brands and the resourcing of our distribution and marketing network. Manufacturing capacity is sufficient for the foreseeable future and the tobacco harvest met expectations. Sadly, the year was marked with a number of natural disasters, loss of life and hardship and nevertheless we were able to provide assistance for some of those in need. The communities around our operations in Java were spared and our community programmes continued focusing on our employees welfare, on local health, education, the needy, contributions to sustaining civic infrastructure and the sharing of our 60th year celebrations with the community at large. Both the Board of Commissioners and the Board of Directors met throughout the year to conduct reviews of the company’s business performance, risk profile and future plans. The corporate governance section in this report provides full details of these activities. Directors acted responsibly in their individual roles and as a Board in managing the Company toward a satisfactory realization of the business plan and objectives. Quarterly reviews of the Company’s financial accounts were undertaken by the independent Audit Committee. The Nomination and Remuneration function was carried out by the Board of Commissioners and there were no changes to either Boards in 2018. Internal audit risk and control routines protect the integrity of our operations and there were no extraordinary events to report. As this report is being finalized, Indonesia is contemplating forthcoming elections. The appointment of the next Government is an opportunity to raise expectations and make progress with necessary structural change to diversify into value added manufacturing and processing industry with investment in capacity building. A strong and stable banking sector, positive progress in infrastructure development and the emergence of the digital economy offer further bright prospects to broaden the economy and lessen exposure to commodity cycles. In 2018 Gudang Garam celebrated a 60th birthday. We thank our employees, our strategic business partners, shareholders and loyal customers. Sixty years represents an achievement but also an accumulation of wisdom and therefore a sound foundation for the future.",
    content_type: "text/plain",
    consumption_preferences: true
  })
  .then(result => {
    console.log(JSON.stringify(result, null, 2));
    console.log("\n\n\nSummary of the personality: ");
    console.log(getSummary(result));
  })
  .catch(err => {
    console.log("error:", err);
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

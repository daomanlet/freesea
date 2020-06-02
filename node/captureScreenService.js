const puppeteer = require('puppeteer'); 
const express = require('express');


var app = express();
app.get('/', async (req, resp) => {
    const url = req.query.url;
    if (!url) {
        resp.send('Url is required');
        return;
    }
    try {
		imageBuffer = await takeScreenShot(url);
		resp.set({'Content-Type': 'image/jpeg'});
        resp.send(imageBuffer);
    } catch (e) {
        resp.send(e.message);
    }
});

app.listen(3000);

//const url = "https://twitter.com/realDonaldTrump/status/1266800113260703744";
async function takeScreenShot(url) {     
   let browser = await puppeteer.launch({ headless: true });
   let page = await browser.newPage();
   await page.goto(url, { waitUntil: "networkidle0", timeout: 60000 });
   await page.setViewport({ width: 1024, height: 800 });
   await autoScroll(page);
   const imageBuffer = await page.screenshot({
//    path: "./screenshot.jpg",
    type: "jpeg",
    fullPage: true
  });
  await page.close();
  await browser.close();
  return imageBuffer;
} 
//run();


async function autoScroll(page){
    await page.evaluate(async () => {
        await new Promise((resolve, reject) => {
            var totalHeight = 0;
            var distance = 100;
            var timer = setInterval(() => {
                var scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;

                if(totalHeight >= scrollHeight || totalHeight > 10000){
                    clearInterval(timer);
                    resolve();
                }
            }, 100);
        });
    });
}
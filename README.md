# Paypaya

![Cover](/resources/cover.png)
## Inspiration

More money, more problems. 
Lacking an easy, accessible, and secure method of transferring money? Even more problems.

An interesting solution to this has been the rise of WeChat Pay, allowing for merchants to use QR codes and social media to make digital payments.

But where does this leave people without sufficient bandwidth? Without reliable, adequate Wi-Fi,  technologies like WeChat Pay simply aren't options. People looking to make money transfers are forced to choose between bloated fees or dangerously long wait times. 

As designers, programmers, and students, we tend to think about how we can design tech. But how do you design tech for that negative space? During our research, we found of the people that lack adequate bandwidth, 1.28 billion of them have access to mobile service. This ultimately led to our solution: **Money might not grow on trees, but Paypayas do.** 🍈

## What it does

Paypaya is a backend application that allows users to perform simple and safe transfers using SMS.

Users start by texting a toll free number. Doing so opens a digital wallet that is authenticated by their voice. From that point, users can easily transfer, deposit, withdraw, or view their balance. Papaya

Despite being build for low bandwidth regions, Paypaya also has huge market potential in high bandwidth areas as well. Whether you are a small business owner that can't afford a swipe machine or a charity trying to raise funds in a contactless way, the possibilities are endless.

## How we built it

We first set up the application in a Docker container on Google Cloud Run to streamline cross OS development. We then set up a MongoDB collections to be modified by our Flask app. Within the app, we also integrated the Twilio and PayPal APIs to create a digital wallet and perform the application commands. After creating the primary functionality of the app, we implemented voice authentication by collecting voice clips from Twilio to be used in Microsoft Azure.

For our branding and slides, everything was made vector by vector on Figma. 

## Challenges we ran into

Man. Where do we start. Although it was fun, working in a two person team meant that we were both wearing (too) many hats. In terms of technical problems, the PayPal API documentation was archaic, making it extremely difficult for us to call the necessary functions, prompting us to pivot our approach. It was also really difficult to convert the audio from Twilio to binary for the Azure API. Lastly, we had trouble keeping track of conversation state using Python with under the limitation of using a single handler.

## Accomplishments that we're proud of

We're really proud of creating a fully functioning MVP! All of 6 of our moving parts came together to form a working proof of concept. All of our graphics (slides, logo, collages) are all made from scratch. :))

## What we learned

Anson - As a first time back end developer, I learned SO much about using APIs, webhooks, databases, and servers. I also learned that Jacky falls asleep super easily.

Jacky - I learned that Microsoft Azure and Twilio can be a pain to work with and that Google Cloud Run is a blessing and a half. I also learned that two person teams can still do a pretty ok job.

## What's next for Paypaya

More language options! English is far from the native tongue of the world. By expanding the languages available, Paypaya will be accessible to even more people. We would also love to do more with financial planning, providing a log of previous transactions for individuals to track their spending and income.
# TU Film Telegram Bot
> Useful Telegram bot to stay updated about the upcoming schedule for TU Film

Do you also have a group in Telegram where you and your fellow students decide if you are going to the
next movie shown in TU Film? We are in such a group and you often face the same dialogues. Here are a
few examples of such dialogues:

A: *Hey, who's going tonight?* <br />
B: *To what movie?*

A: *Who's going to watch movie X tonight?* <br />
B: *What's movie X about? Is it good?*

A: *Should we meet before?* <br />
B: *When does the movie start?*

This leads to looking up all these things on the TU Film page, Google, or IMDb. With the TU Film bot you can get all this
 information directly into Telegram. See below for a list of all features.

## How to Use

Just add the bot in Telegram. Search for **tufilmbot**. Type '/' to see an overview over
 possible commands.

## Features

* Get information about the next movie, this includes the title, date, link to the movie
on TU Film website, link to IMDb and its rating on IMDb.
* List all upcoming movies. Shown with date and title.
* Subscribe to a reminder which informs you about the next movie. It will remind you
around 11 a.m. on the day of the movie.

## Developing

The bot is written in Python 2.7 and hosted on the Google Cloud Platform. More information
about developing on the Google Cloud Platform with Python can be found [here](https://cloud.google.com/appengine/docs/python/).
To start developing clone this repository to your local workspace.

```shell
git clone https://https://github.com/sebaruehl/tufilmtelegrambot.git tufilmbot
cd tufilmbot/
```

If you want to test the application on Google Cloud Platform you have create a new project
in the [Google Cloud Console](https://console.cloud.google.com/start), a Google account is required.
The app gets all its configuration information out of a yaml file called **app.yaml**.
You can find a sample file in this repository. To get started just rename it and insert
your projects' application id (first line of the file).

```shell
cd tufilmbot/
cp app.yaml.sample app.yaml
```

Furthermore, a own Telegram bot is need for testing the application. Information about how to create
a new one can be found [here](https://core.telegram.org/bots). In the process of creating
the bot you will receive an API-Token. Save this token in a file called **bot.token** in the projects'
main directory.

```shell
cd tufilmbot/
echo API-Token > bot.token
```

Finally you have to set web hook for the bot to the application on Google, call (replace **projectId**
with the one set in your app.yaml file):

https://**projectId**.appspot.com/set_webhook?url=https://**projectId**.appspot.com/webhook

### Deploying / Publishing

For easy deploying use the Google App Engine SDK.
It can be downloaded [here](https://cloud.google.com/appengine/downloads#Google_App_Engine_SDK_for_Python).


## Contributing

If you find any bugs or want additional features feel free to create a new issues. If you have any other questions or concerns
you can also send an email.

If you'd like to contribute, please fork the repository and use a feature
branch. Pull requests are warmly welcome.


## Licensing

The code in this project is licensed under MIT license ([more information](https://opensource.org/licenses/MIT)).

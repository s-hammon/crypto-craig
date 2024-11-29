# crypto-craig

[![python](https://img.shields.io/badge/Python-3.12.7-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)![Deploy](https://github.com/s-hammon/crypto-craig/workflows/ci/badge.svg)

A [Discord.py](https://discordpy.readthedocs.io/en/stable) project. Use `!getprice <coin symbol>` in chat to get the latst price of your favorite crypto. 

## Requirements 

* [Python](https://python.org)
* [Turso](https://turso.tech/)
* A [CoinMarketCap](https://coinmarketcap.com/api/pricing/) API key
* A [Discord Appliation](https://discord.com/developers)

## Running locally

### Setting up the database & crawler

*TODO - create a setup.sh script

1. Clone the repo: 

    ```git clone https://github.com/s-hammon/crypto-craig.git```

1. (in your environment) install requirements: 

    ````pip install -r requirements.txt````

1. Set env vars, install Goose;

    ```source scripts/init.sh```

    #### Env Vars

    * `CMC_PRO_API_KEY` -- your CMC API key
    * `DISCORD_TOKEN` -- your Discord bot's API token (typically done at `https://discord.com/developers/applications/<YOUR-APP-ID>/bot`)
    * `DB_URL` -- Turso database url (`database-username.turso.io`)

        *TODO - reconfigure to allow for local db development/testing*

    * `TURSO_AUTH_TOKEN` -- your Turso API token (recommend using the CLI tool and running `turso auth token`) to run the crawler job
    * `TURSO_AUTH_TOKEN_DISCORD_CLIENT` -- optional second token for the discord app. May be set to the same value as `TURSO_AUTH_TOKEN`

1. Migrate database: 

    ```make up```
    
    or
    
    ```goose -dir sql/schema turso "${DB_URL}?authToken=${TURSO_AUTH_TOKEN}" up```

1. Populate the database with `python3 main.py crawler job`
    - This will query CMC for the latest prices on all coins

### Craig

After inviting your application to your Discord server(s), run the actual Discord bot with `python3 main.py craig`. Supported commands include:

1. `!getprice <coin_symbol>`
1. `!all`
1. `!history <coin_symbol> [range]`

## Deployment

I've created a single Dockerfile whose entrypoint may be overridden to run either the crawler or the bot. You can build an image from this Dockerfile and run them in containers for either job/service.

**Note**: please ensure that you have the aformentioned environment variables set in your development environment!

* Crawler: `docker run --entrypoint "python3 main.py crawler job" <image_name>:<image_tag>`
* Craig: `docker run --entrypoint "python3 main.py craig" <image_name>:<image_tag>`

## Contributing

Your help is greatly appreciated.

Before developing, please ensure that you are on a forked repo. Run `scripts/setup-dev.sh` to ensure that you have `Ruff` and `Goose` installed in your environment. Prior to opening a pull request, your code must pass existing tests and linting. The provided `Makefile` offers a convenient way to run tests (using the `unittest` Python module) and linting:

* Tests: `make test`
* Linting: `make pretty` 
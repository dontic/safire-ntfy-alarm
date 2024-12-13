# safire-ntfy-alarm
Create an alarm server for Safire cameras that send a NTFY push notification to your phone


## Deployment

1. Clone the repo

    ```bash
    git clone https://github.com/dontic/safire-ntfy-alarm.git
    ```

    ```bash
    cd safire-ntfy-alarm
    ```

2. Copy `.env.template` to `.env` and change the ntfy secrets

    ```bash
    cp .env.template .env && nano .env
    ```

    > Use `ctrl`+`x` to save

2. Build the container

    ```bash
    docker build -t safire-ntfy .
    ```

3. Run the container

    ```bash
    docker compose up
    ```

    Or run it in the background:
    ```bash
    docker compose up -d
    ```

4. Configure alarm server

    Go to your safire camera and point the server to `YOUR_IP:5000`

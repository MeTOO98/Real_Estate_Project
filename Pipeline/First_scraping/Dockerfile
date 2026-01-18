FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget unzip xvfb libnss3 libxss1 libasound2 fonts-liberation libappindicator3-1 libatk-bridge2.0-0 libgtk-3-0

RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y

RUN apt-get update && \
    apt-get install -y curl unzip jq && \
    curl -sS https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json \
    | jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform=="linux64").url' \
    | xargs curl -L -o /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /tmp && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY Get_Data_From_Bayut.py .
CMD ["python", "Get_Data_From_Bayut.py"]

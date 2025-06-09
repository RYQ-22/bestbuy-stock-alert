# bestbuy-stock-alert 🤖
Monitors a Best Buy product and sends an alert when it's back in stock.

## ✨ Features

- **Stock Alerts**: Automatically monitors the stock status of a product at a given BestBuy URL and sends a notification when it becomes available
- **Notification Channels**: Supports sending notifications via Twilio for SMS alerts 📱, as well as email notifications through Gmail or iCloud 📧.
- **Lightweight**: Use the single Python script or a simple binary file 🕊️.

## 🚀 Usage

### 1. Set the environment variables

- Modify `bestbuy.env`
- Put `bestbuy.env` and the binary file (or Python script) in the same folder

### 2.1 Run with simple binary file (Recommended)

- Downlaod the binary file in [Releases](https://github.com/RYQ-22/bestbuy-stock-alert/releases) page.
- Grant executable permissions
- `binary_file_name <url>`

### 2.2 Run in Python environment

- Use Python version: 3.9.20
- `pip install -r requirements.txt`
- `python bestbuy.py <url>`

## 🕒 Set as recurring task

### Linux
```
crontab -e
# set 1 to the interval (minute)
# set 7-23 to the active hours
# add next line to the end of the file
*/1 7-23 * * * cd your_folder && ./binary_file_name your_url >> your_logfile 2>&1
```

### Windows
```
# set 1 to the interval (minute)
# set 07:00 to the start time
# set 23:59 to the end time
schtasks /Create /SC MINUTE /MO 1 /TN "BestBuy Stock Alert" /TR "cmd /c \"cd /d \"C:\\Path\\To\\Your\\Folder\" && binary_file_name \"your_url\" >> \"C:\\Path\\To\\Your\\Log\\your_logfile.log\" 2>&1\"" /ST 07:00 /ET 23:59
```

## 📧 Send SMS with email

As an alternative to Twilio, you can send notifications by emailing a special address provided by the recipient's mobile carrier. The email will be delivered as an SMS.

### Common US Carrier Gateways

| Carrier | Gateway Address |
| :--- | :--- |
| **AT&T** | `@txt.att.net` |
| **Verizon** | `@vtext.com` |
| **T-Mobile**| `@tmomail.net` |
| **Sprint**| `@messaging.sprintpcs.com` |
| **Cricket**| `@sms.cricketwireless.net` |
| **U.S. Cellular**| `@email.uscc.net` |

For example, if you want to send SMS to `+1xxxxxxxxxx` with email whose carrier is T-Mobile, the recipient's email address is `xxxxxxxxxx@tmomail.net`

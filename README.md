# bestbuy-stock-alert
Check Best Buy stock and send an SMS notification via Twilio API if available.

## Usage

Python version: 3.9.20

- Modify `bestbuy.env`
- `pip install -r requirements.txt`
- `python bestbuy.py <url>`

## Set as recurring task

### Linux
```
crontab -e
# set 1 to the interval (minute)
# set 7-23 to the active hours
# add next line to the end of the file
*/1 7-23 * * * cd your_folder && your_python_path bestbuy.py your_url >> your_logfile 2>&1
```

### Windows
```
TODO
```
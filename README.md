# Timed power state
A python program to Hibernate, Shutdown, Reboot after a chosen delay.
⚠ Windows only

![Image of the interface](https://i.ibb.co/rH2Y5Gr/python-hhepj-Oca-WN.png)


I'm using the [Sun Valley ttk theme](https://github.com/rdbende/Sun-Valley-ttk-theme) by rdbende

Don't hesitate to [open an issue](https://github.com/MrPowley/timed_power_state/issues/new) to report a bug or ask a question, I'm open to everyone

## Features
- Hibernate, shutdown or reboot
- Send power signal after a desired delay hh:mm:ss (00:00:00 for no delay)
- Execute custom command before power signal (File copy, video conversion...)
- Look for custom text in command output to send power signal (Sees "finished" in output -> shuts down)
- Can abort at any time
- Can be hid to tray (Right click > Show, in tray)
- Can recognise and exact image on screen
- Can save and load presets (Need restart)

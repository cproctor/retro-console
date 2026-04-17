# Backing Up and Cloning the Pi SD Card

Raspberry Pi Imager can't create images from a running Pi — it only writes pre-made images to cards. Use `dd` instead.

## Step 1: Image the SD card

Shut down the Pi and insert the SD card into a Mac. Find the device:

```bash
diskutil list
```

Image it (replace `disk2` with the correct device):

```bash
sudo dd if=/dev/rdisk2 of=~/retro-console.img bs=4m status=progress
```

## Step 2: Shrink the image (recommended)

By default the image is the full size of the SD card, even if most of it is empty. [PiShrink](https://github.com/Drewsif/PiShrink) shrinks it to only the used space and makes it auto-expand on first boot. Run it on Linux (or in a Linux VM/container on Mac):

```bash
sudo pishrink.sh retro-console.img retro-console-small.img
```

## Step 3: Write to a new card

Use Raspberry Pi Imager to write the `.img` file to a new SD card, or use `dd`:

```bash
sudo dd if=~/retro-console.img of=/dev/rdisk3 bs=4m status=progress
```

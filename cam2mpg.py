import os
import subprocess
import calendar
import datetime
import sys
import tarfile
import logging as log
from shutil import rmtree
from optparse import OptionParser, OptionGroup


def main():
    for cam in os.listdir(os.getcwd()):
        if os.path.isdir(cam):
            # Get yesterday's date, or use user provided date if specified
            user_date = [None, None, None, None]
            if opts.date:
                user_date = opts.date.split("/")
                if len(user_date) != 4:
                    log.critical("--dir option requires a path with exactly four components e.g. Front_Cam/2013/Jan/04_Fri , terminating")
                    sys.exit()
            TODAY = datetime.date.today()
            YESTERDAY = TODAY - datetime.timedelta(days=1)
            weekday = calendar.weekday(YESTERDAY.year, YESTERDAY.month, YESTERDAY.day)
            abbr_weekday = user_date[3] or "%02d_%s" % (YESTERDAY.day, calendar.day_abbr[weekday])
            # Construct a path to yesterday
            DATE_LEAF = "%s//%s//%s//%s//%s" % (
                    os.getcwd(),
                    user_date[0] or cam,
                    user_date[1] or YESTERDAY.year,
                    user_date[2] or calendar.month_abbr[YESTERDAY.month],
                    abbr_weekday
                    )
            log.debug("Entering: %s" % (DATE_LEAF))
            # Exit here if we can't find the directory
            if os.path.exists(DATE_LEAF):
                os.chdir(DATE_LEAF)
            else:
                log.critical("Directory %s does not exist, terminating" % (DATE_LEAF))
                sys.exit()
            
            files = os.listdir(DATE_LEAF)
            files.sort()

            left_split = os.path.join(os.path.split(DATE_LEAF)[0])
            backup_path = os.path.join(left_split, ".backup")
            tar_path = os.path.join(backup_path, "%s.tar.gz" % (abbr_weekday))

            # Exit here if any files are already renamed (i.e. from a previous bad run)
            if not opts.force:
                for i in files:
                    if i.startswith("img"):
                        log.critical("%s is in an undersirable state and requires manual intervention, terminating" % (DATE_LEAF))
                        if os.path.exists(tar_path):
                            log.critical("Consider restoring from backup file and then run script again: %s" % (tar_path))
                        else:
                            log.critical("If the files are all renamed correctly in sequence, run the script with the --force switch")
                        sys.exit()
            # Create a backup
            if not opts.skip:
                if not os.path.exists(backup_path):
                    log.debug("Creating backup directory: %s" % (backup_path))
                    os.mkdir(backup_path)
                log.debug("Creating backup: %s" % (tar_path))
                tar_file = tarfile.open(tar_path, "w:gz")
                for i in files:
                    tar_file.add(i)
                tar_file.close()

            # Rename files into an ffmpeg-friendly format
            if not opts.force:
                c = 1
                for i in files:
                    if i.endswith("jpg"):
                        log.debug("Renaming %s to img%d.jpg" % (i, c))
                        os.rename(i, "img%d.jpg" % (c))
                    c += 1

            # Encode files with ffmpeg
            try:
                log.debug("Encoding video to %s.mp4" % (os.path.join(os.path.split(os.getcwd())[0], abbr_weekday)))
                subprocess.call(["ffmpeg",
                                "-f",
                                "image2",
                                "-r",
                                "1",
                                "-vcodec",
                                "mjpeg",
                                "-i",
                                "img%d.jpg",
                                "-vcodec",
                                "libx264",
                                "%s.mp4" % (os.path.join(os.pardir, abbr_weekday))],
                            stderr=open(os.devnull, "w"),
                            stdout=open(os.devnull, "w"))
                os.chdir(os.pardir)
                if not opts.keep:
                    log.debug("Removing directory: %s" % (abbr_weekday))
                    rmtree(abbr_weekday)
            except:
                pass
            # Test that everything went fine
            final_file_path = os.path.join(left_split, "%s.mp4" % (abbr_weekday))
            for i in [final_file_path, tar_path]:
                if os.path.exists(i):
                    log.info("%s successfully created" % (i))
                else:
                    log.critical("Failed to create %s" % (i))
            
if __name__ == "__main__":
    parser = OptionParser()
    danger = OptionGroup(parser, "Advanced options", "These options should \
never need to be used in most use cases and may cause data loss. Only \
use if you know what you are doing.")
    parser.add_option("-v",
            "--verbose",
            action="store_true",
            dest="verbose",
            default=False,
            help="Print detailed progress information")
    parser.add_option("-d",
            "--dir",
            action="store",
            dest="date",
            help="Operate on a specific directory e.g. Front_Cam/2013/Jan/04_Fri"
            )
    danger.add_option("-s",
            "--skip-backup",
            action="store_true",
            dest="skip",
            help="Skip gzip-compressed backup archive creation"
    )
    danger.add_option("-f",
            "--force",
            action="store_true",
            dest="force",
            default=False,
            help="Force ffmpeg to run on a dirty directory (implies -s)"
            )
    parser.add_option("-k",
            "--keep-files",
            action="store_true",
            dest="keep",
            default=False,
            help="Don't remove source image files when encoding is completed"
            )
    parser.add_option_group(danger)
    (opts, args) = parser.parse_args()
    if opts.force:
        opts.skip = True

    log_level = log.INFO
    if opts.verbose:
        log_level = log.DEBUG
    log.basicConfig(stream=sys.stderr, format="%(levelname)s: %(message)s", level=log_level)
    
    
    main()
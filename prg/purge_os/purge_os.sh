#!/bin/bash

journalctl_day=3
archivemail_day=3
short_server_name="bonnezic"
my_year=`date "+%Y"`
my_month=`date "+%m"`
my_day=`date "+%d"`
my_hour=`date "+%H"`
my_minute=`date "+%M"`
my_seconde=`date "+%S"`
yyyymmdd_hhmmss=$my_year$my_month$my_day"_"$my_hour$my_minute$my_seconde

set -eu
LANG=en_US.UTF-8 snap list --all | awk '/disabled/{print $1, $3}' |
	while read snapname revision; do
		snap remove "$snapname" --revision="$revision"
	done
set +eu
rm /var/lib/snapd/cache/*

dpkg -l 'linux-*' | sed '/^ii/!d;/'"$(uname -r | sed "s/\(.*\)-\([^0-9]\+\)/\1/")"'/d;s/^[^ ]* [^ ]* \([^ ]*\).*/\1/;/[0-9]/!d' | xargs sudo apt-get -y purge

apt-get autoremove -y

apt-get clean -y

journalctl_dayd=$journalctl_day"d"
journalctl --vacuum-time=$journalctl_dayd

zip_name=$short_server_name"_mail_"$yyyymmdd_hhmmss".zip"
zip_folder="/home/backup/mail/"
zip_files=$zip_folder"*.*"
mkdir -p $zip_folder
find $zip_files -mtime +$archivemail_day -exec rm {} \;
zip -r -j $zip_folder$zip_name "/var/mail/"
rm -rf /var/mail/*



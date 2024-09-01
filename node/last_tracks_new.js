const http = require('http');
const fs = require('fs-extra');
const moment = require('moment-timezone');
const cron = require('node-cron');
const { title } = require('process');
const { exec } = require('child_process');
const util = require('util');
const execAsync = util.promisify(require('child_process').exec);
const path = require('path');
const mm = require('music-metadata');

const port = 3003;
const lastTrackSystemFile = "/home/web/bonnezic.com/last_tracks_new.json";
const lastTrackFolder = "/home/web/bonnezic.com/_zic_new/";
const imgMusicFolder = "/home/web/bonnezic.com/img_music/";
const albumFolder = "/home/web/bonnezic.com/album/";
const generalImgFolder = "/home/web/bonnezic.com/images_square/";
let clients = []; // This will store all active SSE connections

const server = http.createServer((req, res) => {
    if (req.url === '/tracks' && req.method === 'GET') {
        res.writeHead(200, {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*',
        });

        const clientId = Date.now();
        const newClient = { id: clientId, res };
        clients.push(newClient);

        loadTracks().then(tracks => {
            res.write(`data: ${JSON.stringify(tracks)}\n\n`);
        });

        const heartbeatInterval = setInterval(() => {
            res.write(':heartbeat\n\n');
        }, 15000);

        req.on('close', () => {
            console.log(`Client ${clientId} disconnected.`);
            clearInterval(heartbeatInterval);
            clients = clients.filter(client => client.id !== clientId);
        });
    } else {
        res.writeHead(404, {'Content-Type': 'text/plain'});
        res.end('Not Found');
    }
});

function aaaammjjhhmmss() {
    return moment().tz("Europe/Paris").format('YYYYMMDDHHmmss');
}

function getFormattedDateTime() {
    return moment().tz("Europe/Paris").format('YYYY-MM-DD HH:mm:ss');
}

function getCompactDateTime() {
    return moment().tz("Europe/Paris").format('YYYYMMDD_HHmmss');
}
async function loadTracks() {
    try {
        return await fs.readJson(lastTrackSystemFile);
    } catch (error) {
        console.error('Error loading tracks:', error);
        return [];
    }
}

function checkTrackInJson(finalTitle, tracks) {
    const found = tracks.some(track => track.name === finalTitle);
    return found ? "ok" : "ko";
}

async function getMp3Duration(mp3_file) {
    try {
      const metadata = await mm.parseFile(mp3_file);
      const duration = metadata.format.duration;
  
      const minutes = Math.floor(duration / 60);
      const seconds = Math.floor(duration % 60);
  
      const formattedDuration = `${minutes}:${seconds.toString().padStart(2, '0')}`;
  
      return formattedDuration;
    } catch (err) {
      console.error('Error getting MP3 duration:', err.message);
      return "0:00";
    }
  }
  
  

async function getCurrentTrack() {
    try {
        const { stdout: filePath } = await execAsync('mpc -f %file% | head -1');
        const fileName = path.basename(filePath.trim());
        const finalTitleTmp = fileName.replace(/\.mp3$/, '');
        const finalTitle = finalTitleTmp.replace(/(^\w|\s\w)/g, match => match.toUpperCase());


        let artist = "No Artist", title = "No Title", album = "No Album";

        try {
            const { stdout: artistStdout } = await execAsync('mpc -f %artist% | head -1');
            artist = artistStdout.trim();
            if (artist.length > 39) {
                artist = artist.substring(0,39) + "..."     
            }
        } catch {}

        try {
            const { stdout: titleStdout } = await execAsync('mpc -f %title% | head -1');
            title = titleStdout.trim();
            if (title.length > 69) {
                title = title.substring(0,69) + "..."     
            }
        } catch {}

        try {
            const { stdout: albumStdout } = await execAsync('mpc -f %album% | head -1');
            album = albumStdout.trim();
        } catch {}
		
		try {
            const { stdout: FullFileNameStdout } = await execAsync('mpc -f %file% | head -1');
            FullFileName = FullFileNameStdout.trim();
        } catch {}
		
		if (artist== "No Artist") {
			if (finalTitle.textOf("-")>0) { 
				finalTitle_arr = finalTitle.split("-");
				artist = finalTitle_arr[0].trim();
				title = finalTitle_arr[1].trim();
			} else {
				artist = finalTitle.trim();
				title = "";
			}
		}
		
        return { finalTitle, filePath: filePath.trim(), artist, title, album, FullFileName };
    } catch (error) {
        console.error('Error executing mpc command:', error);
        throw error;  // Propagate the error
    }
}

async function processTracks() {
    try {
      const tracks = await loadTracks();
      const { finalTitle, filePath, artist, title, album, FullFileName } = await getCurrentTrack(); // Destructure the object
      console.log('trackInfo :', finalTitle);
  
      const result = checkTrackInJson(finalTitle, tracks);
      const dh = aaaammjjhhmmss(); // Define dh here, to ensure it's available wherever needed
  
      if (result === "ok") {
        console.log('current track in jsonTrack');
      } else {
        console.log('New track detected, updating...');
        const dateTime = getFormattedDateTime();
        const dateTimeCompact = getCompactDateTime();
        const trackId = "bonnezic_" + dateTimeCompact;
        const extractFolderName = filePath => path.basename(path.dirname(filePath));
        const playlist = path.basename(path.dirname(filePath));
        const mp3_filename = trackId + ".mp3";
        const zic_file = lastTrackFolder + mp3_filename;
        await fs.copyFile(filePath, zic_file);  // Use filePath correctly
        exec(`setfacl -m u:www-data:rX -R ${zic_file}`);
        console.log('File copied!');
        let imgUrl;
        let imgFile = albumFolder + finalTitle + ".jpg";
        if (!await fs.pathExists(imgFile)) {
          imgFile = imgMusicFolder + finalTitle + ".jpg";
          if (!await fs.pathExists(imgFile)) {
            const imgFiles = await fs.readdir(generalImgFolder);
            const randomImgFile = imgFiles[Math.floor(Math.random() * imgFiles.length)];
            imgUrl = `https://bonnezic.com/images_square/${randomImgFile}?${dh}`;
          } else {
            imgUrl = `https://bonnezic.com/img_music/${finalTitle}.jpg?${dh}`;
          }
        } else {
          imgUrl = `https://bonnezic.com/album/${finalTitle}.jpg?${dh}`;
        }
  
        const duration = await getMp3Duration(filePath);
  
        const newTrack = {
          date: dateTime,
          file: mp3_filename,
          name: finalTitle,
          artist: artist,
          title: title,
          album: album,
          playlist: playlist,
          duration: duration,
          img_url: imgUrl,
		  filename: FullFileName
        };
        tracks.unshift(newTrack);
        exec(`cd ${lastTrackFolder} && ls -t | tail -n +11 | xargs rm --`);
        console.log('File removed!');
        if (tracks.length > 10) tracks.splice(10); // Keep only the latest 10 tracks
        console.log('Write Json File !');
        await fs.writeJson(lastTrackSystemFile, tracks, { spaces: 2 });
  
        // Notify all clients about the update
        clients.forEach(client => {
          client.res.write(`data: ${JSON.stringify(tracks)}\n\n`);
        });
      }
    } catch (error) {
      console.error('Error processing tracks:', error);
    }
  }

cron.schedule('*/5 * * * * *', processTracks);
server.listen(port, () => console.log(`Server running on http://localhost:${port}`));

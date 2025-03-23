document.addEventListener('DOMContentLoaded', function() {
  // Find the container which has the data-release attribute
  const container = document.querySelector('.audio-player-container');
  const releasePath = container.getAttribute('data-release');
  
  // Change tracks.json to playlist.json
  const playlistPath = releasePath;
  
  let tracks = [];
  let currentTrack = 0;
  let isPlaying = false;
  let isRepeat = false;
  let availableFormats = [];
  let currentFormat = ''; // Will be set after loading tracks
  
  // Fetch the playlist JSON
  fetch(playlistPath)
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to load playlist');
      }
      return response.json();
    })
    .then(data => {
      tracks = data;
      
      // Extract available formats from the first track
      if (tracks.length > 0 && tracks[0].format) {
        availableFormats = Object.keys(tracks[0].format);
        
        // Set binaural as default format if available
        if (availableFormats.includes('Binaural') || availableFormats.includes('BIN')) {
          currentFormat = availableFormats.includes('Binaural') ? 'Binaural' : 'BIN';
        } else {
          currentFormat = availableFormats[0]; // Fallback to first format if binaural not available
        }
        
        init(); // Initialize the player after loading tracks
      }
    })
    .catch(error => {
      console.error('Error loading playlist:', error);
      document.getElementById('track-title').textContent = 'Error loading playlist';
      document.getElementById('track-artist').textContent = 'Please check console for details';
    });
  
  // Add format selector to the UI - dynamically based on available formats
  function addFormatSelector() {
    const formatDownloadContainer = document.createElement('div');
    formatDownloadContainer.className = 'format-download-container';
    
    const formatSelector = document.createElement('div');
    formatSelector.className = 'format-selector';
    
    // Create format display names map
    const formatDisplayNames = {
      'Binaural': 'Binaural',
      'BIN': 'Binaural',
      'UHJ Stereo': 'UHJ Stereo',
      'UHJ': 'UHJ Stereo',
      'TRANSAURAL': 'Transaural',
      'Transaural': 'Transaural',
      'Ambisonic': 'Ambisonic',
      'AMBISONIC': 'Ambisonic',
      '3OA': 'Ambisonic'
      // Add more mappings as needed
    };
    
    // Generate options based on available formats
    let optionsHTML = '';
    availableFormats.forEach(format => {
      const displayName = formatDisplayNames[format] || format;
      const selected = format === currentFormat ? 'selected' : '';
      optionsHTML += `<option value="${format}" ${selected}>${displayName}</option>`;
    });
    
    formatSelector.innerHTML = `
      <label for="format-select">Audio Format</label>
      <select id="format-select">
        ${optionsHTML}
      </select>
    `;
    
    // Create download button
    const downloadBtn = document.createElement('button');
    downloadBtn.id = 'download-btn';
    downloadBtn.className = 'download-btn';
    downloadBtn.innerHTML = '<i class="fas fa-download"></i> Téléchargement';
    
    // Add download functionality
    downloadBtn.addEventListener('click', function() {
      downloadCurrentTrack();
    });
    
    // Add components to container
    formatDownloadContainer.appendChild(formatSelector);
    formatDownloadContainer.appendChild(downloadBtn);
    
    // Insert the container before the playlist
    document.querySelector('.playlist-container').prepend(formatDownloadContainer);
    
    // Add event listener to format selector
    document.getElementById('format-select').addEventListener('change', function() {
      changeFormat(this.value);
    });
  }
  
  // Add this function for downloading the current track
  function downloadCurrentTrack() {

    const container = document.querySelector('.audio-player-container');
    const download_path = container.getAttribute('download-path');
    
    // Create a temporary link element
    const downloadLink = document.createElement('a');
    downloadLink.href = download_path;
    
    // Append to body, trigger click and remove
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
  }
  
  // Initialize playlist
  function initPlaylist() {
    const playlist = document.getElementById('playlist');
    playlist.innerHTML = '';
    
    tracks.forEach((track, index) => {
      const li = document.createElement('li');
      li.className = index === currentTrack ? 'active' : '';
      
      const trackTitle = track.titletrack;
      
      li.innerHTML = `
        <div class="track-info">
          <span class="track-title">${trackTitle}</span>
          <span class="track-artist">${track.artist}</span>
        </div>
        <span class="track-duration">--:--</span>
      `;
      
      li.addEventListener('click', function() {
        playTrack(index);
      });
      
      playlist.appendChild(li);
    });

    // Preload track durations without playing them
    preloadTrackDurations();
  }

  // Preload track durations without playing them
  function preloadTrackDurations() {
    tracks.forEach((track, index) => {
      const playlistItems = document.querySelectorAll('#playlist li');
      if (playlistItems[index]) {
        const durationElement = playlistItems[index].querySelector('.track-duration');
        if (durationElement) {
          durationElement.textContent = formatTime(track.duration);
        }
      }
      
      // If this is the current track, update the total time display
      if (index === currentTrack) {
        document.getElementById('total-time').textContent = formatTime(track.duration);
      };
    });
  }

  // Update active track in playlist
  function updateActiveTrack() {
    const playlistItems = document.querySelectorAll('.playlist li');
    playlistItems.forEach((item, index) => {
      if (index === currentTrack) {
        item.classList.add('active');
      } else {
        item.classList.remove('active');
      }
    });
  }

  // Update progress bar
  function updateProgress() {
    if (tracks[currentTrack].howl && tracks[currentTrack].howl.playing()) {
      const seek = tracks[currentTrack].howl.seek() || 0;
      document.getElementById('current-time').textContent = formatTime(seek);
      
      const progress = (seek / tracks[currentTrack].howl.duration()) * 100 || 0;
      document.getElementById('progress').style.width = progress + '%';
      
      requestAnimationFrame(updateProgress);
    }
  }

  // Format time in seconds to MM:SS
  function formatTime(secs) {
    const minutes = Math.floor(secs / 60) || 0;
    const seconds = Math.floor(secs - minutes * 60) || 0;
    return minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
  }

  // Generate a simple waveform visualization
  function generateWaveform() {
    const waveformElement = document.getElementById('waveform');
    waveformElement.innerHTML = '';
    
    const bars = 50; // Number of bars in the waveform
    
    for (let i = 0; i < bars; i++) {
      const bar = document.createElement('div');
      bar.className = 'waveform-bar';
      
      // Generate random height for demo purposes
      const height = Math.floor(Math.random() * 100) + 20;
      bar.style.height = height + '%';
      
      waveformElement.appendChild(bar);
    }
  }

  // Change audio format
  function changeFormat(format) {
    if (format === currentFormat) return;
    
    const wasPlaying = isPlaying;
    const currentSeek = tracks[currentTrack].howl ? tracks[currentTrack].howl.seek() : 0;
    
    // Stop current playback
    if (isPlaying && tracks[currentTrack].howl) {
      tracks[currentTrack].howl.stop();
    }
    
    // Update format
    currentFormat = format;
    
    // Clear howl instances to force recreation with new format
    tracks.forEach(track => {
      track.howl = null;
    });
    
    const trackTitle = tracks[currentTrack].titletrack;
    
    // Show format indicator in UI
    document.getElementById('track-title').textContent = `${trackTitle}`;
    
    // Update playlist to reflect the new format
    initPlaylist();
    
    // Resume playback if it was playing before
    if (wasPlaying) {
      playTrack(currentTrack, currentSeek);
    }
  }
  
  // Stop all playing tracks except the one with specified index (if provided)
  function stopAllTracks(exceptIndex) {
    tracks.forEach((track, index) => {
      if (track.howl && track.howl.playing() && index !== exceptIndex) {
        track.howl.stop();
      }
    });
  }
  
  // Play a track
  function playTrack(index, seek = 0) {
    // Stop all currently playing tracks except the one we're about to play
    stopAllTracks(index);
    
    // Update current track
    currentTrack = index;
    
    const trackTitle = tracks[currentTrack].titletrack;
    
    // Update UI
    updateActiveTrack();
    document.getElementById('track-title').textContent = `${trackTitle}`;
    document.getElementById('track-artist').textContent = tracks[currentTrack].artist;
    
    // Generate waveform before playing
    generateWaveform();
    
    // Create Howl instance if not created or if it was unloaded
    if (!tracks[currentTrack].howl) {
      tracks[currentTrack].howl = new Howl({
        src: [tracks[currentTrack].format[currentFormat]],
        html5: true,
        volume: document.getElementById('volume-slider').value / 100,
        onplay: function() {
          isPlaying = true;
          document.getElementById('play-btn').innerHTML = '<i class="fas fa-pause"></i>';
          requestAnimationFrame(updateProgress);
        },
        onpause: function() {
          isPlaying = false;
          document.getElementById('play-btn').innerHTML = '<i class="fas fa-play"></i>';
        },
        onstop: function() {
          isPlaying = false;
          document.getElementById('play-btn').innerHTML = '<i class="fas fa-play"></i>';
          document.getElementById('progress').style.width = '0%';
          document.getElementById('current-time').textContent = '0:00';
        },
        onend: function() {
          if (isRepeat) {
            playTrack(currentTrack);
          } else if (currentTrack < tracks.length - 1) {
            playTrack(currentTrack + 1);
          } else {
            tracks[currentTrack].howl.stop();
          }
        },
        onload: function() {
          document.getElementById('total-time').textContent = formatTime(tracks[currentTrack].howl.duration());
          
          // Update playlist duration
          const playlistItems = document.querySelectorAll('.playlist li');
          if (playlistItems[currentTrack]) {
            const durationElement = playlistItems[currentTrack].querySelector('.track-duration');
            if (durationElement) {
              durationElement.textContent = formatTime(tracks[currentTrack].howl.duration());
            }
          }
        }
      });
    }
    
    // If there's already a duration loaded (from preload), update the display
    if (tracks[currentTrack].duration) {
      document.getElementById('total-time').textContent = formatTime(tracks[currentTrack].duration);
    }
    
    // Update play button state immediately before playing
    isPlaying = true;
    document.getElementById('play-btn').innerHTML = '<i class="fas fa-pause"></i>';
    
    // Play the track
    tracks[currentTrack].howl.play();
    
    // Start progress update immediately
    requestAnimationFrame(updateProgress);
    
    // Seek to position if specified
    if (seek > 0) {
      tracks[currentTrack].howl.seek(seek);
    }
  }
  
  // Progress bar click event
  document.getElementById('progress-bar').addEventListener('click', function(e) {
    if (tracks[currentTrack]?.howl) {
      const percent = e.offsetX / this.offsetWidth;
      const seekPosition = percent * tracks[currentTrack].howl.duration();
      
      // Update audio position
      tracks[currentTrack].howl.seek(seekPosition);
      
      // Update the progress bar immediately
      document.getElementById('progress').style.width = (percent * 100) + '%';
      
      // Update the current time display immediately
      document.getElementById('current-time').textContent = formatTime(seekPosition);
    }
  });

  // Initialize
  function init() {
    if (tracks.length === 0) {
      console.error('No tracks available');
      return;
    }
    
    initPlaylist();
    addFormatSelector();

    const trackTitle = tracks[currentTrack].titletrack;
    
    document.getElementById('track-title').textContent = `${trackTitle}`;
    document.getElementById('track-artist').textContent = tracks[0].artist;
    
    // Set up event listeners for player controls
    document.getElementById('play-btn').addEventListener('click', function() {
      if (isPlaying) {
        tracks[currentTrack].howl.pause();
      } else {
        playTrack(currentTrack);
      }
    });
    
    document.getElementById('prev-btn').addEventListener('click', function() {
      if (currentTrack > 0) {
        playTrack(currentTrack - 1);
      }
    });
    
    document.getElementById('next-btn').addEventListener('click', function() {
      if (currentTrack < tracks.length - 1) {
        playTrack(currentTrack + 1);
      }
    });
    
    document.getElementById('volume-slider').addEventListener('input', function() {
      const volume = this.value / 100;
      
      // Update volume icon
      const volumeIcon = document.getElementById('volume-icon');
      if (volume === 0) {
        volumeIcon.className = 'fas fa-volume-mute';
      } else if (volume < 0.5) {
        volumeIcon.className = 'fas fa-volume-down';
      } else {
        volumeIcon.className = 'fas fa-volume-up';
      }
      
      // Set volume on current track
      if (tracks[currentTrack].howl) {
        tracks[currentTrack].howl.volume(volume);
      }
    });
    
    document.getElementById('repeat-btn').addEventListener('click', function() {
      isRepeat = !isRepeat;
      this.classList.toggle('active');
    });
  }
});
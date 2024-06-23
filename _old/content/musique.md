---
title: Musique
type: landing

sections:
  - block: slider
    content:
      slides:
        - title: Outwards
          content: 'Projet musical principal, entre rock alternatif et rock progressif.'
          align: center
          background:
            image:
              # Specify an image from `assets/media/`
              # or delete the image section to remove it
              filename: musique/ow.jpg
              filters:
                brightness: 0.7
            # position: center
            color: '#555'
          link:
            icon: house
            icon_pack: fas
            text: Site web
            url: 'https://outwardsmusic.com'
        - title: 🍔💥 Burger Bang
          content: Titres improvisés, à la sauce du moment.
          align: center
          background:
            image:
              # Specify an image from `assets/media/`
              # or delete the image section to remove it
              filename: musique/bb.jpg
              filters:
                brightness: 0.7
            position: right
            color: '#666'
          link:
            icon: youtube
            icon_pack: fab
            text: Youtube
            url: 'https://youtube.com/playlist?list=PL5VxlMwmaE1HteIDI0E2ph0T1CZ9WVBul'
    design:
      # Slide height is automatic unless you force a specific height (e.g. '400px')
      slide_height: ''
      # Make the slides full screen within the browser window?
      is_fullscreen: true
      # Automatically transition through slides?
      loop: false
      # Duration of transition between slides (in ms)
      interval: 2000
---
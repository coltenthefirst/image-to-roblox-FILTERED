<!---
Copyright 2024 Colten Wade Parker. All rights reserved.

Licensed under the MIT License;
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-->

# This Source Code Is Really Outdated... Updating Very Soon!

<p align="center">
  <img alt="Images To Roblox Parts" src="https://i.postimg.cc/MGx8XrT6/Roblox-Logo-2022.jpg" width="422" height="422" style="max-width: 100%;">
  <br/>
  <br/>
</p>

<h6 align="center">
    ~ Works For IOS, Android, Windows, Mac, and Console. ~
</h6>

<h6 align="center">
    ~ Please note that some images can get bypassed. ~
</h6>

<h1 align="center">
    <a href="https://github.com/coltenthefirst/image-to-roblox">
        <img alt="License Info" src="https://img.shields.io/badge/License-MIT-blue.svg">
    </a>
    <a href="https://github.com/coltenthefirst/image-to-roblox-FILTERED/releases">
        <img alt="Newest Release" src="https://img.shields.io/github/release/coltenthefirst/image-to-roblox-FILTERED.svg">
    </a>
</h1>

<p align="center">
  <img alt="asset" src="https://cdn.vectorstock.com/i/500p/16/54/checkerboard-black-and-white-background-vector-33401654.jpg" width="5000" height="10" style="max-width: 100%;">
  <br/>
  <br/>
</p>

<h1 align="center">
    Images To Roblox Parts (NSFW DETECTOR VERSION)
</h1>

<br>

<p align="center">
  <img alt="asset" src="https://cdn.vectorstock.com/i/500p/16/54/checkerboard-black-and-white-background-vector-33401654.jpg" width="5000" height="10" style="max-width: 100%;">
  <br/>
  <br/>
</p>

# THERE IS A ISSUE WITH MODEL-2F! PLEASE READ [fix](https://github.com/coltenthefirst/image-to-roblox/issues/5) TO FIX IT!

## Introduction

This repository contains the backend source code for the **Image To Parts** Roblox Game. This tool allows users to convert image URLs into parts within Roblox. Users are free to use the files provided in this repository for their own purposes.

## How It Works
Here’s a overview of the process:
1. Input an image URL and select a quality setting (such as mid, high, low, extra low).
2. The image URL and selected quality are sent to **Vercel**.
3. Vercel checks the image for nsfw and if its sfw than Vercel downloads the image and runs a Python script based on your selection.
4. A Lua script is generated and sent back to Roblox, where it is processed into parts that resemble the pixels of your image.

## To-Do List

<h6 style="text-align: right;">
    ~ EXPECT THESE TO CHANGE!!! ~
</h6>

### Current Tasks

- [ ] PlaceHolder

### Completed Tasks

- [x] NSFW Filter (Github/Model-2F)
- [x] Frame By Frame Animation Player (Model-2)
- [x] Faster Image Gen Speed (Model-2)
- [x] Enhanced image data privacy (Github)
- [x] Improved support for black and white images and single-color images (Github)
- [x] Add a frame-by-frame animation player (Model-2)
- [x] Add a delete button for parts (Model-2)
- [x] Fix Error 500 (Github/Model-2)
- [x] Resolve issue with the first pixel not generating (Model-2)

## Videos
[Model-1](https://www.youtube.com/watch?v=oFm_znA53r8)
[Model-2](https://www.youtube.com/watch?v=6pRmz4_hoDo)

## Game Links
- [Create Your Dreams](https://www.roblox.com/games/128560311364952/Create-Your-Dreams) (unfiltered btw)


You can download the place files here:

| Model / Update                            | Download |
|------------------------------------|--------|
| Update 2/Model-2 (FILTERED VERSION): |[Google Drive Link](https://drive.google.com/file/d/1aW_yDFl51jWNuYRXIWO-meuBk5S-00I3/view?usp=sharing)|


## Uploading Custom Images
For obtaining direct image urls, I recommended to use [Postimages.org](https://postimages.org/) to obtain a direct link. Other services can be used as long as they provide a direct link.

## Tested Image Services
- ✅ = Works
- ❌ = Does not work

| Service                            | Status |
|------------------------------------|--------|
| [Postimages.org](https://postimages.org/)      | ✅     |
| [imgbb.com](https://imgbb.com/)                | ✅     |
| [i.imghippo.com](https://i.imghippo.com)       | ✅     |
| [i.imgur.com](https://i.imgur.com)             | ❌     |
| [imgbox.com](https://imgbox.com/)              | ✅     |
| [snipboard.io](https://snipboard.io/)          | ✅     |
| [prnt.sc](https://prnt.sc/)                    | ❌     |
| [lunapic.com](https://www7.lunapic.com/editor/?action=quick-upload) | ✅     |
| [imagevenue.com](https://www.imagevenue.com/)  | ✅     |
| [pictr.com](https://pictr.com/upload)          | ✅     |

## FAQ

**Q: Do my uploaded images get logged?**  
**A:** Uploaded images are temporary logged, they cannot be downloaded, viewed, or anything, unless its in Roblox.

**Q: What type images does this filter?**  
**A:** Gore, Violence, Sexual Content, and Cuss Word types too.

**Q: What are the chances of a image bypassing detection?**  
**A:** A probability range of 5% to 12%.

# Exploit Content Model:
https://api4.ai/apis/nsfw
```
curl -X GET -G 'https://api.sightengine.com/1.0/check.json' \
    -d 'models=text-content' \
    -d 'api_user=1726990225&api_secret=YGaA9jJn5sipbN5TC3GDBD7YJro5UnZx' \
    --data-urlencode 'url=https://sightengine.com/assets/img/examples/example7.jpg'
```

# Exploit Words Model:
https://dashboard.sightengine.com/getstarted
```
curl -X "POST" \
  "https://demo.api4ai.cloud/nsfw/v1/results" \
  -F "url=https://storage.googleapis.com/api4ai-static/samples/nsfw-1.jpg"
```

## License
This project is licensed under the MIT License. You are free to use, modify, and distribute the files in this repository, as long as you include the original license. For more details, see the [LICENSE](LICENSE) file.

## Contributing
Contributions are welcome. If you have suggestions or improvements, please open an issue or submit a pull request.

This is a guide for AI to scrape the data in apps_temp.html and format it into a JSON file that can be used in the workflow.
The data is from the SetApp website, which lists various apps available in their subscription service.

The JSON file should have the following structure:

```json
[
  {
    "uid": 742,
    "title": "Supercharge",
    "subtitle": "Supercharge your Mac",
    "iconSrc": "https://setapp.com/cdn-cgi/image/quality=75,format=auto,width=80/https://store.setapp.com/app/742/44858/icon-1758668179-68d32593df0c6.png",
    "arg": "https://setapp.com/apps/supercharge",
    "rating": 100,
    "platforms": "Mac",
    "status":"",
    "ai": ""
  },
  ...
]
```

Where the HTML file contains multiple app entries, each with the following data points:
```html
<a class="application-card_applicationCard__Xj9Ue" href="/apps/supercharge">
    <div class="stack_stack__Z0wzO stack_display-block__3QclE stack_direction-row__N9lsC stack_align-stretch__kIsuv stack_justify-start__7Oa1K stack_wrap-no__OKKu0 stack_gap-4-sm__VCv7W stack_gap-4-md__t7IW_ stack_gap-4__ZLt_o">
        <div class="stack_stack__Z0wzO stack_display-block__3QclE stack_direction-row__N9lsC stack_align-center__yHiRm stack_justify-center__aFcOj stack_wrap-no__OKKu0 stack_gap-0__CP5MD application-card-icon-section_iconWrapper__AYhUC application-card-icon-section_sizeMd__dxmr9 application-card_appIcon__Nnuc4">
            <span class="badge_root___qdsk badge_sm__mJaZ4 font-size-1 application-card_badge__clXBn" style="--badge-background:var(--bg-accent-dark-pink-5)" data-color="success">AI+</span>
            <img alt="Supercharge" draggable="false" loading="lazy" width="80" height="80" decoding="async" data-nimg="1" class="" style="color:transparent" srcSet="https://store.setapp.com/cdn-cgi/image/width=96,quality=75,format=auto/app/742/46849/icon-1777789220-69f6e92451312.png 1x, https://store.setapp.com/cdn-cgi/image/width=256,quality=75,format=auto/app/742/46849/icon-1777789220-69f6e92451312.png 2x" src="https://store.setapp.com/cdn-cgi/image/width=256,quality=75,format=auto/app/742/46849/icon-1777789220-69f6e92451312.png"/>
        </div>
        <div>
            <h3 class="heading_h4__sNApT application-card_applicationName__Jha3u">Supercharge</h3>
            <div class="stack_stack__Z0wzO stack_display-block__3QclE stack_direction-column__QgQQx stack_align-stretch__kIsuv stack_justify-start__7Oa1K stack_wrap-no__OKKu0 stack_gap-2-sm__W8qN9 stack_gap-2-md__hWW0U stack_gap-2__xvXbb">
                <div class="application-card_description__pFqXu">Supercharge your Mac</div>
                <div class="application-card_cardInfo__v5AUF">
                    <svg viewBox="0 0 16 16" class="application-card_ratingIcon__IAsPT" width="16" height="16">
                        <path d="M5.45401 12.1429V7.47214C5.45401 6.68657 5.64622 5.91276 6.01407 5.21386L7.99845 1.44571C8.14228 1.1721 8.43186 1 8.74816 1C9.21339 1 9.59079 1.3671 9.59079 1.81962V5.95238H13.0892C14.3996 5.95238 15.3205 7.20719 14.8948 8.4131L13.3642 12.7464C13.0994 13.4961 12.3739 14 11.5586 14H7.3633C6.30874 14 5.45401 13.1686 5.45401 12.1429ZM0.999023 7.50002C0.999023 6.64511 1.71119 5.9524 2.59009 5.9524C3.469 5.9524 4.18116 6.64511 4.18116 7.50002V12.4524C4.18116 13.3073 3.469 14 2.59009 14C1.71119 14 0.999023 13.3073 0.999023 12.4524V7.50002Z"></path>
                    </svg>
                    <span>100
                        <!-- -->
                    %</span>
                    <span class="application-card_separator__rpNwW">•</span>
                    <span class="application-card_platforms__TE0vT">Mac</span>
                </div>
            </div>
        </div>
    </div>
</a>
```

- The uid can be scraped from the image URL, which contains the app ID (e.g., `742` for Supercharge).
ie. "https://store.setapp.com/cdn-cgi/image/width=256,quality=75,format=auto/app/742/46849/icon-1777789220-69f6e92451312.png" -> uid = 742
- title can be scraped from the `<h3>`
- subtitle from the `<div>` with a class like the following: class="application-card_description..."
- iconSrc is the image URL
- arg can be constructed from the href attribute of the `<a>` tag.
- rating can be scraped from the span containing the percentage,
- platforms can be scraped from the corresponding span as well.
- status can be scraped from the badge span if it exists, "New" otherwise set to empty string.
- ai can be scraped from the badge span if it exists, "AI+", otherwise set to empty string.

Take the scraped data and place it into a new JSON file "apps_scraped.json" with the structure shown above.
The JSON file should contain an array of app objects, each with the fields: uid, title, subtitle, iconSrc, arg, rating, platforms, status, and ai. as in the main apps.json file used in the workflow.

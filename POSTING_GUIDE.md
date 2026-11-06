# TasteDesk daily post: run guide

One Armenian post per day about one TasteDesk feature, published to Instagram and Facebook through Buffer.

## Buffer

- Organization "My organization": `6ac67899def251d7c9f85b1e`
- Instagram tastedesk.am: `6ac6791f6a5c39ccb642c01f` (metadata `{"instagram": {"type": "post", "shouldShareToFeed": true}}`)
- Facebook TasteDesk page: `6ac679416a5c39ccb642c12e` (metadata `{"facebook": {"type": "post"}}`)
- Publish with `mode: "shareNow"`, `schedulingType: "automatic"`, same text and image on both.
- Image URL: `https://raw.githubusercontent.com/gbmikaelian/tastedesk-social/main/posts/<file>.png` (push before posting, then confirm it returns 200).

## Picking the feature

Take the first feature in `features.json` whose `id` does not appear in `posted.json`, skipping any feature marked `"minor": true` (minor features are never a post of their own; they are supporting points inside their related posts). When every non-minor feature has been posted, start again from the top with a new angle (different hook, headline, cards and theme than the earlier post for that feature, see `posted.json`).

Allowed facts: the feature's `brief` plus the briefs of the features listed in its `related`. Use the related briefs to show how the feature works across the whole system (customer side, staff/kitchen/courier side, owner side). Never invent numbers, timings, customer counts, prices or capabilities that are not in those briefs.

## Scenario first

A post is a scenario, not a feature tour. Pick one concrete moment in a restaurant's day and show how TasteDesk handles it end to end, connecting the feature with its related features (for example: item goes on the iiko stop list, disappears from the site by itself, the customer only orders what exists; or a guest scans the table QR, the order lands on the same board as phone and site orders, the ticket prints in the kitchen). Show the smart part, the thing that happens automatically or across roles. Never present UI fields, form inputs or status names as the selling point.

## Photo (background)

Every post uses the photo layout with a freshly generated photo:

1. Figma file "TasteDesk social backgrounds": fileKey `PXpnTCwgP3pmVBzUcELek8`. Call Figma `create_session` with that fileKey first, then `generate_image` with that fileKey, the sessionId, width 1024, height 1280.
2. Prompt pattern: "Candid lifestyle photo, vertical 4:5. <who, where, what they are doing, emotion>. <lighting>, shallow depth of field, natural skin tones, shot on 35mm, realistic, not staged. The upper third of the frame is a calm, darker, out-of-focus background with empty space for text. No text, no logos, no visible screen content."
3. The scene must show the moment from the scenario: a guest at a table scanning a QR, someone at home ordering on the sofa, a cook pulling a ticket from the kitchen printer, a courier at an apartment entrance checking the phone, an owner at the bar counter looking at the phone after closing, a cashier taking a phone order, friends sharing burgers, etc. People in their 20s to 50s who could plausibly be in Yerevan. Food must be from the Burgery menu (burgers, pizza, latte, cake, cola).
4. Vary it: the setting (restaurant hall / home / kitchen / street / counter), the person and the time of day must differ from the last 3 entries' `scene` in `posted.json`.
5. Download `image.url` with curl to `bg/<YYYY-MM-DD>-<id>.jpg` path in the spec as `"photo"` (save as .png if the URL is png). If generation or download fails twice, fall back to the old theme layout (set `"theme"` instead of `"photo"`, themes: night, ember, ocean, grape, cream, mint, graphite).
6. Look at the image (Read it). Reject and regenerate (max 2 extra tries) if there is gibberish text, a visible fake UI, extra fingers or broken hands, or if the top third is too busy for the headline.

## Spec file

Write `specs/<YYYY-MM-DD>-<id>.json`, then render with
`python3 -I tools/render_post.py specs/<date>-<id>.json posts/<date>-<id>.png`.

```json
{
  "feature": "<id>",
  "photo": "bg/<date>-<id>.png",
  "accent": [253, 186, 116],
  "headline": ["White first line", "Accent second line"],
  "subline": "One short supporting line",
  "cards": [
    {"title": "...", "sub": "...", "color": "green|amber|blue|red|purple", "icon": "check|bike|bell|card|star|clock|printer|qr|pin|chart"}
  ]
}
```

- `accent` (RGB) colors the second headline line and the TasteDesk badge. Pick one that suits the photo: warm photos `[253,186,116]`, cool/night `[125,211,252]`, green `[52,211,153]`, pink `[240,171,252]`, yellow `[250,204,21]`.
- Headline = the result for the owner in plain words ("Վերջացածը կայքում չի երևում", "Սեղանից պատվեր՝ առանց մատուցողի"). Not a UI description.
- 1 or 2 cards (2 by default). Card 1 = the trigger (what the customer or staff did), card 2 = what the system did automatically / what the other role sees. Never form fields.
- Length limits: headline lines up to 20 characters, subline up to 48, card title up to 26, sub up to 40.
- Armenian only in headline and cards, except brand names (iiko, QR, TasteDesk), numbers, ֏ and the restaurant domain.
- Example data must be plausible Burgery data: Burgery, 6 Arshakunyats Ave, real menu items (Crispy Chicken Burger 2 600 ֏, Double Cheeseburger 3 600 ֏, Classic Beef Burger 2 800 ֏, Pepperoni Pizza 3 900 ֏, Margherita Pizza, Latte 2 000 ֏, Chocolate Cake 1 800 ֏, Coca-Cola 700 ֏). Never show a real customer's name or phone.

After rendering, open the PNG and check it: no clipped or trailing-"…" text, cards do not cover a face, headline readable over the photo, Armenian renders correctly. Fix the spec and re-render if needed.

## Caption

Armenian, written like a founder who knows restaurants explains the product to another owner: concrete, confident, no pathos, no em dashes, no slogans. 600 to 1100 characters before the hashtags.

1. Hook (1 to 2 lines, one emoji): the same concrete moment the photo shows: who, when, what goes wrong without TasteDesk. Not a generic question.
2. How it works in TasteDesk (2 to 4 sentences): walk through the real flow end to end, what the customer does, what staff / kitchen / courier see, how it connects to the related features. Name real statuses, screens and roles from the briefs.
3. What changes for the owner (1 to 2 sentences): the business result, from the briefs only.
4. CTA line: `📩 Գրեք մեզ DM՝ անվճար դեմոյի համար։`
5. Hashtags on the last line: `#TasteDesk #YerevanRestaurants` plus 2 or 3 Armenian tags that fit the feature.

Do not:
- list form fields or UI elements as if they were benefits ("separate fields for floor and apartment" is a detail inside the flow, not a selling point);
- use a ✅ checklist (at most one short list of up to 3 outcomes, only if it reads better than prose);
- repeat the headline as the closing line, or end on a slogan;
- reuse a hook or opening scene from `posted.json`.

Quality bar, example for `address-autocomplete` (structure and depth, do not copy):

> Երեկոյան պիկին պատվերը պատրաստ է, իսկ առաքիչը շենքի մոտ կանգնած զանգում է հաճախորդին՝ պարզելու, թե որ մուտքն է 📞
>
> TasteDesk-ում հաճախորդը հասցեն գտնում է ավտոմատ որոնումով, նշում քարտեզի վրա և լրացնում մուտքը, հարկը, բնակարանը ու հեռախոսահամար՝ հենց առաքիչի համար։ Առաքման գինը հաշվարկվում է ըստ գոտու և հեռավորության ու երևում է checkout-ում՝ պատվիրելուց առաջ։ Առաքիչն իր էկրանին տեսնում է պատրաստ պատվերները ամբողջական հասցեով, նշում է «Ճանապարհին» և «Առաքված», իսկ հաճախորդը ամեն քայլին հետևում է live։
>
> Ձեզ համար սա նշանակում է ավելի քիչ զանգեր ու վեճեր առաքման գնի շուրջ, և առաքիչը ճիշտ դուռը գտնում է առաջին անգամից։

## After publishing

Append an entry to `posted.json` (date, feature, scene (one short English line: who, where, time of day), photo, image, spec, both Buffer post ids, caption_hook), commit and push.

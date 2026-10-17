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

## Theme (background)

The renderer has these themes: `night` (dark green), `ember` (warm red/orange), `ocean` (deep blue), `grape` (purple), `cream` (light warm), `mint` (light green), `graphite` (dark with yellow).
Set `"theme"` in the spec. It must differ from the themes of the last 3 entries in `posted.json` (entries without a `theme` field count as `night`). Alternate dark and light: if the previous post was dark (night, ember, ocean, grape, graphite), prefer a light one (cream, mint) and vice versa, unless that breaks the last-3 rule. Prefer warm themes (ember, cream) for customer/food features and cool ones (ocean, graphite, mint) for restaurant/back-office features.

## Spec file

Write `specs/<YYYY-MM-DD>-<id>.json`, then render with
`python3 -I tools/render_post.py specs/<date>-<id>.json posts/<date>-<id>.png`.

```json
{
  "feature": "<id>",
  "theme": "ember",
  "headline": ["White first line", "Accent second line"],
  "subline": "One short supporting line",
  "front": "screens/....png",
  "back": "screens/....png",
  "badge": {"file": "screens/02-product.png", "crop": [80, 0, 540, 460]},
  "cards": [
    {"title": "...", "sub": "...", "color": "green|amber|blue|red|purple", "icon": "check|bike|bell|card|star|clock|printer|qr|pin|chart"}
  ]
}
```

- Use the feature's `front`/`back` from `features.json`. Omit both for the cards-only layout. `badge` only works with both phones.
- Headline = the result for the restaurant owner (fewer calls, no lost tickets, orders straight from the table), not a description of the UI.
- Exactly 3 cards that read like live app notifications and tell one story across roles: card 1 what the customer does, card 2 what the restaurant / kitchen / courier sees, card 3 the result. Never three form fields or three UI labels.
- Length limits so text stays large: headline lines up to 22 characters each, subline up to 45.
  With phones: card title up to 18 characters, sub up to 28. Cards-only: title up to 26, sub up to 44.
- Armenian only in headline and cards, except brand names, numbers, ֏ and the restaurant domain.
- Example data must be plausible Burgery data: Burgery, 6 Arshakunyats Ave, real menu items (Crispy Chicken Burger 2 600 ֏, Double Cheeseburger 3 600 ֏, Classic Beef Burger 2 800 ֏, Pepperoni Pizza 3 900 ֏, Margherita Pizza, Latte 2 000 ֏, Chocolate Cake 1 800 ֏, Coca-Cola 700 ֏). Never show a real customer's name or phone.

After rendering, open the PNG and check it: no clipped or trailing-"…" text, nothing overlapping the headline, Armenian renders correctly, text readable on the chosen theme. Fix the spec and re-render if needed.

## Caption

Armenian, written like a founder who knows restaurants explains the product to another owner: concrete, confident, no pathos, no em dashes, no slogans. 600 to 1100 characters before the hashtags.

1. Hook (1 line, one emoji): a concrete scene from a restaurant's day that this feature fixes: who, when, what goes wrong. Not a generic question.
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

Append an entry to `posted.json` (date, feature, theme, image, spec, both Buffer post ids, caption_hook), commit and push.

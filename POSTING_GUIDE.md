# TasteDesk daily post: run guide

One Armenian post per day about one TasteDesk feature, published to Instagram and Facebook through Buffer.

## Buffer

- Organization "My organization": `6ac67899def251d7c9f85b1e`
- Instagram tastedesk.am: `6ac6791f6a5c39ccb642c01f` (metadata `{"instagram": {"type": "post", "shouldShareToFeed": true}}`)
- Facebook TasteDesk page: `6ac679416a5c39ccb642c12e` (metadata `{"facebook": {"type": "post"}}`)
- Publish with `mode: "shareNow"`, `schedulingType: "automatic"`, same text and image on both.
- Image URL: `https://raw.githubusercontent.com/gbmikaelian/tastedesk-social/main/posts/<file>.png` (push before posting, then confirm it returns 200).

## Picking the feature

Take the first feature in `features.json` whose `id` does not appear in `posted.json`. When every feature has been posted, start again from the top with a new angle (different hook, headline and cards than the earlier post for that feature, see `posted.json`).

## Spec file

Write `specs/<YYYY-MM-DD>-<id>.json`, then render with
`python3 -I tools/render_post.py specs/<date>-<id>.json posts/<date>-<id>.png`.

```json
{
  "feature": "<id>",
  "headline": ["White first line", "Green second line"],
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
- Exactly 3 cards. They should read like live app notifications that tell the feature's story.
- Length limits so text stays large: headline lines up to 22 characters each, subline up to 45.
  With phones: card title up to 18 characters, sub up to 28. Cards-only: title up to 26, sub up to 44.
- Armenian only in headline and cards, except brand names, numbers, ֏ and the restaurant domain.
- Example data must be plausible Burgery data: Burgery, 6 Arshakunyats Ave, real menu items (Crispy Chicken Burger 2 600 ֏, Double Cheeseburger 3 600 ֏, Classic Beef Burger 2 800 ֏, Pepperoni Pizza 3 900 ֏, Margherita Pizza, Latte 2 000 ֏, Chocolate Cake 1 800 ֏, Coca-Cola 700 ֏). Never show a real customer's name or phone.

After rendering, open the PNG and check it: no clipped or trailing-"…" text, nothing overlapping the headline, Armenian renders correctly. Fix the spec and re-render if needed.

## Caption

Armenian, natural and short, the way a founder would write it, no pathos, no em dashes.

1. Hook line with one emoji, ideally a pain the restaurant owner recognises.
2. One or two short sentences, or 3 to 5 lines starting with ✅.
3. CTA line: `📩 Գրեք մեզ DM՝ անվճար դեմոյի համար։`
4. Hashtags on the last line: `#TasteDesk #YerevanRestaurants` plus 2 or 3 Armenian tags that fit the feature.

Only state facts from the feature's `brief`. No prices other than the menu examples, no numbers or customer counts that are not in the brief. Do not reuse a hook from `posted.json`.

## After publishing

Append an entry to `posted.json` (date, feature, image, spec, both Buffer post ids, caption_hook), commit and push.

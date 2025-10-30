<!-- 7bffa348-b594-4a31-a971-66fa182b2d35 79a7497e-5056-4664-8258-77e6186e80a7 -->
# Update popup to handle product and size

## Scope

- Change `pop_up.py` to:
  - Accept `product_name` parameter
  - Track `selected_size` via internal state
  - Wire size buttons to update `selected_size`
  - On Add: if `product_name == "Red Velvet" and selected_size == "Large"`, briefly display image then close; otherwise add immediately and close.
- Change `order.py` to pass `product_name` for at least one item button (wire `button_13` as “Red Velvet”, others remain generic).

## pop_up.py essential edits

- Function signature:
  - From: `def show_options_popup(parent, on_add_item=None)`
  - To: `def show_options_popup(parent, on_add_item=None, product_name=None)`
- State:
  - `selected_size = {"value": None}`
- Size buttons:
  - Regular button `command=lambda: selected_size.update({"value": "Regular"})`
  - Large button `command=lambda: selected_size.update({"value": "Large"})`
- Add button logic:
  - If Red Velvet + Large: load `image_1.png` into the popup, show it, then `top.after(300, top.destroy)` and call `on_add_item`.
  - Else: call `on_add_item` and `top.destroy()` immediately.

Minimal code sketch for Add button:

```python
 def on_add():
     if on_add_item:
         on_add_item({
             "name": product_name or "Chocolate",
             "size": selected_size.get("value") or "Regular",
             "price": 29.00 if (selected_size.get("value") != "Large") else 39.00,
             "qty": 1,
         })
     if product_name == "Red Velvet" and selected_size.get("value") == "Large":
         top._rv_image_obj = PhotoImage(file=relative_to_assets("image_1.png"))
         canvas.create_image(200.0, 130.0, image=top._rv_image_obj)
         top.after(300, top.destroy)
     else:
         top.destroy()
```

## order.py minimal wiring

- Update one product button (e.g., `button_13`) `command=lambda: show_options_popup(window, on_add_item=add_item_to_cart, product_name="Red Velvet")`.

## Todos

- update-popup-signature: Accept `product_name` in `show_options_popup`
- track-size-state: Add and use `selected_size` and wire buttons
- add-button-logic: Implement conditional image display and closing
- wire-order-button: Pass `product_name` for Red Velvet from one product button

### To-dos

- [ ] Accept product_name in show_options_popup
- [ ] Track selected_size and wire size buttons
- [ ] Add conditional image display for Red Velvet Large, then close
- [ ] Pass product_name for Red Velvet from order.py (one button)
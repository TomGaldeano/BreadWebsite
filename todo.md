Tier 2 — Backend logic, no schema changes
Change admin to superadmin, allow making admins (todo #20) — Add is_admin column to User, update admin_required decorator to check is_admin, add UI for superadmin to promote users.
Add settings page for admin and users to create preferences (todo #5) — Simple preferences stored in session or new UserPreference table.
Tier 3 — DB schema additions, moderate complexity
Add inventory column to ingredients and view/controllers (todo #8) — Add stock (Float) column to Ingredient. New admin view to manage stock.
Update inventory management logic when ordering + stats (todo #9) — Deduct ingredient stock when order placed; add inventory log table; stock stats page.
Add delivery notes to user profile (todo #2) — Add delivery_notes column to User. Show/edit on profile. Popup when ordering.
Add option when ordering: send to address, add address, or use location (todo #4) — Order form enhancement with delivery option selector, JS geolocation, address display.
Add email verification option in settings for admin (todo #10) — Admin toggle for requiring email verification; send verification email link.
Add option to send email to admin with payment/order info for the day (todo #17) — Admin button/cron to trigger email via Flask-Mail.
Tier 4 — Complex new features
Add staff database with views and timetable management (todo #12) — New Staff model, timetable views, admin CRUD.
Add delivery guy option that calculates route (todo #13) — DeliveryPerson model, route calculation UI using existing haversine logic.
Add script to order for legacy users (todo #14) — Admin page/form to place orders on behalf of legacy users.
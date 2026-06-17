-- "List each active user with their role name."
-- The grain is one row per active user. The role is reached through a real column=column
-- join predicate (r.id = u.role_id); the status check is a filter, not the join.
SELECT u.id, r.name FROM users u JOIN roles r ON r.id = u.role_id WHERE u.status = 'active';

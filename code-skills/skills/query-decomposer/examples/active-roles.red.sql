-- "List each active user with their role name."
-- Looks joined — the WHERE filters on status. But there is NO join predicate between
-- users and roles, so this is an implicit cross join: every active user × every role.
SELECT u.id, r.name FROM users u, roles r WHERE u.status = 'active';

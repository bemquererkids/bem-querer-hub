-- Create the storage bucket 'chat-media'
insert into storage.buckets (id, name, public)
values ('chat-media', 'chat-media', true)
on conflict (id) do nothing;

-- Set up security policies for the bucket
-- Allow public read access
create policy "Public Access"
  on storage.objects for select
  using ( bucket_id = 'chat-media' );

-- Allow authenticated (or anon for now if easier, but preferably auth) uploads
-- Assuming the backend/frontend uses anon key for upload currently
create policy "Allow Uploads"
  on storage.objects for insert
  with check ( bucket_id = 'chat-media' );

CREATE TABLE IF NOT EXISTS settings (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  goal INTEGER NOT NULL DEFAULT 10,
  reward TEXT NOT NULL DEFAULT 'Café grátis à sua escolha',
  program TEXT NOT NULL DEFAULT 'Um café, um carinho.',
  image TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS customers (
  token TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL DEFAULT '',
  visits INTEGER NOT NULL DEFAULT 0,
  month TEXT NOT NULL,
  created TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  customer TEXT NOT NULL,
  token TEXT NOT NULL,
  visits INTEGER NOT NULL,
  goal INTEGER NOT NULL,
  reward TEXT NOT NULL,
  created TEXT NOT NULL
);
INSERT OR IGNORE INTO settings(id,goal,reward,program,image)
VALUES(1,10,'Café grátis à sua escolha','Um café, um carinho.','');

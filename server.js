import express from 'express';
import { exec } from 'child_process';

const app = express();


app.get('/run-manual-collection', (_, res) => {
  exec('node ./src/collect-manual-names.mjs', { cwd: 'C:/Users/mateo/WebstormProjects/scrape-manuals.cjs' }, (err, stdout, stderr) => {
    if (err) {
      console.error(stderr);
      return res.status(500).send({ error: stderr });
    } else {
      console.log(stdout);
      return res.send({ success: true, output: stdout });
    }
  });
});

app.get('/', (req, res) => {
  res.send('Serveur en ligne !');
});
const PORT = process.env.PORT || 3001;

app.listen(PORT, () => {
  console.log(`Serveur prêt sur http://localhost:${PORT}`);
});

app.get("/test", (req, res) => {
  res.json({ message: "✅ Requête bien reçue depuis n8n !" });
});



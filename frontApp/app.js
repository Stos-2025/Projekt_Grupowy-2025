const express = require('express');
const bodyParser = require('body-parser');
const sqlite3 = require('sqlite3').verbose();
const { exec } = require('child_process');
const path = require('path');

const app = express();
const port = 3000;

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));
const db = new sqlite3.Database('database.sqlite');

db.serialize(() => {
    db.run(`CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        input TEXT,
        time_limit INTEGER,
        memory_limit INTEGER,
        expected_output TEXT,
        output TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )`);
});

app.post('/api/submit-code', (req, res) => {
    const { code, input, timeLimit, memoryLimit, expectedOutput } = req.body;
    db.run(`INSERT INTO submissions (code, input, time_limit, memory_limit, expected_output) VALUES (?, ?, ?, ?, ?)`,
        [code, input, timeLimit, memoryLimit, expectedOutput], 
        function(err) {
            if (err) {
                return res.status(500).json({ error: 'Failed to save submission' });
            }
            
            //db.run(`UPDATE submissions SET output = ? WHERE id = ?`, [output, this.lastID]);
            const insertedId = this.lastID;
            res.json({ id: insertedId });
        });
});

app.get('/api/submissions', (req, res) => {
    const query = `SELECT * FROM submissions`;
    
    db.all(query, [], (err, rows) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        res.json({
            data: rows
        });
    });
});

app.get('/api/submissions/:id', (req, res) => {
    const submissionId = req.params.id;
    const query = `SELECT * FROM submissions WHERE id = ?`;
    
    db.get(query, [submissionId], (err, row) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (!row) {
            return res.status(404).json({ error: 'Zgłoszenie nie znalezione' });
        }
        res.json({
            submission: row
        });
    });
});

app.get('/api/submissions/:id/code', (req, res) => {
    const submissionId = req.params.id;
    const query = `SELECT code FROM submissions WHERE id = ?`;
    
    db.get(query, [submissionId], (err, row) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (!row) {
            return res.status(404).json({ error: 'Zgłoszenie nie znalezione' });
        }
        res.send(row.code);
    });
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});

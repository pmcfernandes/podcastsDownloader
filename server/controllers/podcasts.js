const path = require('path');
const { exec } = require("child_process");

/**
 * Get all podcasts
 */
function getPodcasts(req, res) {
    let sql = `SELECT * FROM podcasts`;

    req.db.all(sql, [], (err, rows) => {
        if (err) {
            res.status(404).json({ success: false, data: '404' });
        } else {
            if (rows.length === 0) {
                res.json([]);
            } else {
                res.json(rows);
            }
        }
    });
};


/** 
 * Get one podcasts
*/
function getPodcast(req, res) {
    let id = parseInt(req.params.id);
    let sql = `
        SELECT COUNT(podcasts_items.id) as total, podcasts.* 
        FROM podcasts_items 
            INNER JOIN podcasts ON podcasts.id = podcasts_items.podcast_id 
        WHERE podcast_id = '${id}'
    `;

    req.db.all(sql, [], (err, rows) => {
        if (err) {
            res.status(404).json({ success: false, data: '404' });
        } else {
            if (rows.length === 0) {
                res.json({});
            } else {
                res.json(rows[0]);
            }
        }
    });
}

/**
 * Delete podcast
 */
function deletePodcasts(req, res) {
    let id = parseInt(req.params.id);
    let sql = `DELETE FROM podcasts WHERE id = ${id}`;

    req.db.all(sql, [], (err, rows) => {
        if (err) {
            res.status(404).json({ success: false, data: '404' });
        } else {
            res.status(200).json({ success: true, data: '200 OK!' });
        }
    });
}

function addPodcasts(req, res) {
    let postData = req.body;
    let id = parseInt(postData.id);

    exec(path.join(path.dirname(__dirname), "...", `pod.bat add ${id}`), (err, stdout, stderr) => {
        if (err) {
            res.status(404).json({ success: false, data: '404' });
        } else if (stderr) {
            res.status(404).json({ success: false, data: '404' });
        } else {
            req.db.all(`SELECT MAX(id) as id FROM podcasts`, [], (err2, rows) => {
                if (err2 || rows.length === 0) {
                    res.status(404).json({ success: false, data: '404' });
                } else {
                    res.status(200).json({
                        success: true, 
                        data: {
                            id: rows[0].id
                        }
                    });
                }
            });
        }
    });
}

module.exports = { getPodcasts, getPodcast, addPodcasts, deletePodcasts };    
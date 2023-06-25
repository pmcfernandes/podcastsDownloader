const express = require('express');
const router = express.Router();
const controller = require('../controllers/podcasts');

router.get('/', controller.getPodcasts);
router.get('/:id', controller.getPodcast);
router.put('/add', controller.addPodcasts);
router.delete('/:id', controller.deletePodcasts);

module.exports = router;
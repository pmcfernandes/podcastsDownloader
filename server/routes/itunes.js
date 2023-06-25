const express = require('express');
const router = express.Router();
const controller = require('../controllers/itunes');

router.get('/search', controller.search);

module.exports = router;
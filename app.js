const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');
const app = express();

// Connect to MongoDB
mongoose.connect('mongodb://localhost:27017/dishesDB', { useNewUrlParser: true, useUnifiedTopology: true });

const dishSchema = new mongoose.Schema({
    heading: String,
    dishes: [String]
});

const Dish = mongoose.model('Dish', dishSchema);

app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));
app.set('view engine', 'ejs');

// Routes
app.get('/', (req, res) => {
    res.render('form');
});

app.post('/submit', async (req, res) => {
    const { heading, ...dishes } = req.body;
    try {
        const headings = Array.isArray(heading) ? heading : [heading];
        const dishEntries = Object.keys(dishes);

        await Dish.deleteMany({});

        for (let i = 0; i < headings.length; i++) {
            const headingName = headings[i];
            const dishList = dishEntries
                .filter(key => key.startsWith(`dish-${i + 1}`))
                .flatMap(key => dishes[key] || []);

            const newDish = new Dish({ heading: headingName, dishes: dishList });
            await newDish.save();
        }

        res.redirect('/display');
    } catch (err) {
        console.log(err);
        res.sendStatus(500);
    }
});

app.get('/display', async (req, res) => {
    try {
        const dishes = await Dish.find({});
        res.render('display', { dishes: dishes });
    } catch (err) {
        console.log(err);
        res.sendStatus(500);
    }
});

app.get('/edit/:id', async (req, res) => {
    try {
        const dish = await Dish.findById(req.params.id);
        if (!dish) return res.status(404).send('Dish not found');
        res.render('edit', { dish: dish });
    } catch (err) {
        console.log(err);
        res.sendStatus(500);
    }
});

app.get('/convert/:id', async (req, res) => {
    try {
        const dish = await Dish.findById(req.params.id);
        if (!dish) return res.status(404).send('Dish not found');

        // Generate PDF using puppeteer
        const html = `
            <h2>${dish.heading}</h2>
            <ul>
                ${dish.dishes.map(d => `<li>${d}</li>`).join('')}
            </ul>
        `;

        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        await page.setContent(html);
        const buffer = await page.pdf({ format: 'A4' });
        await browser.close();

        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', `attachment; filename=dishes-${dish._id}.pdf`);
        res.send(buffer);
    } catch (err) {
        console.log(err);
        res.sendStatus(500);
    }
});
app.post('/update/:id', async (req, res) => {
    try {
        const { heading, dishes } = req.body;
        await Dish.findByIdAndUpdate(req.params.id, { heading: heading, dishes: dishes });
        res.redirect('/display');
    } catch (err) {
        console.log(err);
        res.sendStatus(500);
    }
});


app.listen(3000, () => {
    console.log('Server started on port 3000');
});

const express = require('express');
const router = express.Router();
var request = require('request-promise');
const mysql = require('mysql2');
const dra = require('date-range-array')
const dbconfig = require('../config/database.js');


router.post('/', async function (req, res) {
    let title_list = [];
    const pool = mysql.createPool(dbconfig);
    const promisepool = pool.promise();
    async function review_input(review, categorie, keyword) {
        for (let i = 0; i < review.length; i++) {
            await title_list.push({
                title: review[i].title,
                type: categorie,
                keyword: keyword,
                lat: review[i].lat,
                lng: review[i].lng,
                recomm : review[i].recomm,
                region : review[i].region
            })
        }
    }

    //test_case()
    async function together_input(type, region) {
        let query_data = [];
        console.log(region.length)
        for (let i = 0; i < region.length; i++) {
            query_data.push({
                food: await promisepool.query(`SELECT * FROM food_info where region = "${region[i]}"`),
                hotel: await promisepool.query(`SELECT * FROM hotel_info where region = "${region[i]}"`),
                tour: await promisepool.query(`SELECT * FROM tour_info where region = "${region[i]}"`)
            })
        }
        await review_input(query_data[0].food[0], "food", type)
        await review_input(query_data[0].hotel[0], "hotel", type)
        await review_input(query_data[0].tour[0], "tour", type)

    }

    
    let name = req.cookies.data.name;
    let date1 = req.cookies.data.firstday;
    let date2 = req.cookies.data.lastday;
    let country1 = req.cookies.data.country;
    let dates = dra(date1, date2);
    let datelength = dates.length;
    let country;
    let region = [];
    let keyword = [];
    if (typeof (req.cookies.data.region) === "string") {
        region[0] = req.cookies.data.region;
    } else
        region = req.cookies.data.region;
    if (typeof (req.body.keyword) === "string") {
        keyword[0] = req.body.keyword;
    } else
        keyword = req.body.keyword;

    console.log(keyword);

    let count = 225 / keyword.length;
    count = Math.floor(count);
    for (let i = 0; i < req.body.keyword.length; i++) {
        if (keyword[i] === "짧은이동") {
            let short_dis = [];
            for (let i = 0; i < region.length; i++) {
                const [short] = await promisepool.query(`SELECT short_dis FROM location where region = "${region[i]}" `);
                short_dis.push({
                    "region": short[0].short_dis.split(' ')
                })
            }
            for (let j = 0; j < short_dis.length; j++) {
                region.push(short_dis[j].region[0])
            }
            console.log(region)


        }
        if (keyword[i] === "장거리이동") {
            let long_dis = [];
            for (let i = 0; i < region.length; i++) {
                const [short] = await promisepool.query(`SELECT long_dis FROM location where region = "${region[i]}" `);
                long_dis.push({
                    "region": short[0].long_dis.split(' ')
                })
            }
            for (let j = 0; j < long_dis.length; j++) {
                region.push(long_dis[j].region[0])
            }
            console.log(region)
        }
    }

    let city_query = queryMaker(region);

    if (country1 === "태국") {
        country = "thailand";
    } else if (country1 === "일본") {
        country = "japan";
    } else if (country1 === "베트남") {
        country = "vietnam";
    } else if (country1 === "대만") {
        country = "taiwan";
    } else {
        country = "cambodia";
    }

    //선택한 키워드를 불러올때 req.body.keword[n] 으로 하면 해당하는 키워드 인덱스 값에 맞게 불러옴
    for (let i = 0; i < req.body.keyword.length; i++) {

        if (keyword[i] === "혼자") {
            const alone = await together_input("혼자", region);
            console.log(alone)
        }
        if (keyword[i] === "가족") {
            const family = await together_input("가족", region);
        }
        if (keyword[i] === "친구") {
           const friend = await together_input("친구", region);
        }
        if (keyword[i] === "연인") {
           const couple = await together_input("연인", region);
        }
        if (keyword[i] === "럭셔리") {
            let luxury = `select * from food_info where price =1 and price_score >=4.0 and country = \"${country}\" and region in ( select distinct(region) from food_info where ${city_query}) limit ` + count + `;`;
            let luxury2 = `select * from food_info where recomm LIKE "%고급스러운/비싼%" and recomm LIKE "%분위기%" and country = "${country}" and region in ( select distinct(region) from food_info where ${city_query}) limit ` + count + `;`;
            let luxury3 = `select * from hotel_info where region in ( select distinct(region) from tour_info where ${city_query}) and  price_count >= 250000 limit ` + count + `;`;
            const [luxury_cart] = await promisepool.query(luxury);
            const [luxury_cart2] = await promisepool.query(luxury2);
            const [luxury_cart3] = await promisepool.query(luxury3);

            await review_input(luxury_cart, "food", "럭셔리");
            await review_input(luxury_cart2, "food", "럭셔리");
            await review_input(luxury_cart3, "hotel", "럭셔리");

        }


        if (keyword[i] === "알뜰") {
            let affordable = `select * from food_info where price = 3 and country = "${country}" and region in ( select distinct(region) from food_info where ${city_query}) limit ` + count + `;`;
            let affordable2 = `select * from food_info where recomm LIKE "%가격이싼%" and country = "${country}" and region in ( select distinct(region) from food_info where ${city_query}) limit ` + count + `;`;
            let affordable3 = `select * from hotel_info where region in ( select distinct(region) from tour_info where ${city_query}) and  price_count <= 70000 and price_count != 0 limit ` + count + `;`;

            const [affordable_cart] = await promisepool.query(affordable);
            const [affordable_cart2] = await promisepool.query(affordable2);
            const [affordable_cart3] = await promisepool.query(affordable3);

            await review_input(affordable_cart, "food", "알뜰");
            await review_input(affordable_cart2, "food", "알뜰");
            await review_input(affordable_cart3, "hotel", "알뜰");
        }
        if (keyword[i] === "가성비") {
            let cost_performance = `select * from food_info where price <= 2 and price_score >= 4.0 and country = "${country}" and region in ( select distinct(region) from food_info where ${city_query}) limit ` + count + `;`;
            let cost_performance2 = `select * from food_info where recomm LIKE "%가성비%" and country = "${country}" and region in ( select distinct(region) from food_info where ${city_query}) limit ` + count + `;`;

            const [cp_cart] = await promisepool.query(cost_performance);
            const [cp_cart2] = await promisepool.query(cost_performance2);


            await review_input(cp_cart, "food", "가성비");
            await review_input(cp_cart2, "food", "가성비");

        }
        if (keyword[i] === "많보") {
            let many_look = `select * from tour_info where region in ( select distinct(region) from tour_info where ${city_query}) and title in (select title from tour_info where category LIKE "%콘서트%" or category LIKE "%랜드마크%" or category LIKE "%박물관%"  or category LIKE "%전망대%" or category LIKE "%동물원%" or
            category LIKE "%물길%" or category LIKE "%가든%" or category LIKE "%폭죽%" or category LIKE "%역사%" or category LIKE "%아트%" or category LIKE "%종교%" or category LIKE "%쇼핑%" or
            category LIKE "%해변%" or category LIKE "%전망대%") limit ` + count + `;`;
            let many_look2 = `select * from tour_info where region in ( select distinct(region) from tour_info where ${city_query}) and title in (select title from tour_info where recomm LIKE "%추천관광지%" or recomm LIKE "%쇼핑맛집거리%" or
            recomm LIKE "%문화유적%" or recomm LIKE "%멋진사진촬영지%" or recomm LIKE "%재밌는거리%") limit ` + count + `;`;

            const [ml_cart] = await promisepool.query(many_look);
            const [ml_cart2] = await promisepool.query(many_look2)


            await review_input(ml_cart, "tour", "많보");
            await review_input(ml_cart2, "tour", "많보")

        }
        if (keyword[i] === "많하") {
            let many_do = `select * from tour_info where region in ( select distinct(region) from tour_info where ${city_query}) and title in (select title from tour_info where category LIKE "%하이킹%" or category LIKE "%즐길거리/게임%" or category LIKE "%야외 활동%" or category LIKE "%워터파크&놀이공원%" or category LIKE "%스포츠%" or category LIKE "%바이크 트레일%" or
            category LIKE "%요리 교실%" or category LIKE "%강연&워크숍%" or category LIKE "%밤문화%" or category LIKE "%스키%" or  category LIKE "%모터사이클%") limit ` + count + `;`;
            let many_do2 = `select * from tour_info where region in ( select distinct(region) from tour_info where ${city_query}) and title in (select title from tour_info where recomm LIKE "%놀이공원%" or recomm LIKE "%걷기좋은%") limit ` + count + `;`;
            const [md_cart] = await promisepool.query(many_do);
            const [md_cart2] = await promisepool.query(many_do2);


            await review_input(md_cart, "tour", "많하");
            await review_input(md_cart2, "tour", "많하");

        }
        if (keyword[i] === "많쉬") {
            let many_rest = `select * from tour_info where region in ( select distinct(region) from tour_info where ${city_query}) and title in (select title from tour_info where category LIKE "%물길%" or category LIKE "%자연/공원%" or
            category LIKE "%온천%" or category LIKE "%드라이브%" or category LIKE "%스파%" or category LIKE "%카지노%") limit ` + count + `;`;
            let many_rest2 = `select * from tour_info where region in ( select distinct(region) from tour_info where ${city_query}) and title in (select title from tour_info where recomm LIKE "%힐링하기좋은%") limit ` + count + `;`;


            const [mr_cart] = await promisepool.query(many_rest);
            const [mr_cart2] = await promisepool.query(many_rest2);


            await review_input(mr_cart, "tour", "많쉬");
            await review_input(mr_cart2, "tour", "많쉬");


        }
        if (keyword[i] === "현지") {
            let sql;
            if (country === "thailand") {
                sql = `select * from food_info where food = "타이 요리" and country = "thailand" and region in ( select distinct(region) from food_info where ${city_query}) limit ` + count + `;`;
            } else if (country === "japan") {
                sql = `select * from food_info where food = "일본 요리" and country = "japan" and region in ( select distinct(region) from food_info where ${city_query}) limit ` + count + `;`;
            } else if (country === "vietnam") {
                sql = `select * from food_info where food = "베트남 요리" and country = "vietnam" and region in ( select distinct(region) from food_info where ${city_query}) limit ` + count + `;`;
            } else if (country === "taiwan") {
                sql = `select * from food_info where food = "타이완" and country = "taiwan" and region in ( select distinct(region) from food_info where ${city_query}) limit ` + count + `;`;
            } else {
                sql = `select * from food_info where food = "캄보디아" and country = "cambodia" and region in ( select distinct(region) from food_info where ${city_query}) limit ` + count + `;`;
            }

            const [local_cart] = await promisepool.query(sql);

            await review_input(local_cart, "food", "현지");
        }
        if (keyword[i] === "맛집") {
            let good_taste = `select * from food_info where food_score >= 4.0 and country = "${country}" and region in ( select distinct(region) from food_info where ${city_query}) limit ` + count + `;`;
            let good_taste2 = `select * from food_info where recomm LIKE "%맛집%" and country = "${country}" and region in ( select distinct(region) from food_info where ${city_query}) limit ` + count + `;`;

            const [good_taste_cart] = await promisepool.query(good_taste);
            const [good_taste_cart2] = await promisepool.query(good_taste2);

            await review_input(good_taste_cart, "food", "맛집");
            await review_input(good_taste_cart2, "food", "맛집");
        }
        if (keyword[i] === "밤놀이") {
            let night_play = `select * from food_info where meal_time LIKE "%야간 영업%" and country = "${country}" and region in ( select distinct(region) from food_info where ${city_query}) limit ` + count + `;`;
            let night_play2 = `select * from tour_info where category LIKE "%시장%" and country = "${country}" and region in ( select distinct(region) from food_info where ${city_query}) and working_time in (\n` +
                `select working_time from tour_info where working_time LIKE "%- 오후 10:00%" or working_time LIKE "%- 오후 11:00%" or working_time LIKE "%- 오후 12:00%" ) limit ` + count + `;`;
            let night_play3 = `select * from food_info where recomm LIKE "%저녁식사%" and country = "${country}" and region in ( select distinct(region) from food_info where ${city_query}) limit ` + count + `;`;


            const [night_play_cart] = await promisepool.query(night_play);
            const [night_play_cart2] = await promisepool.query(night_play2);
            const [night_play_cart3] = await promisepool.query(night_play3);

            await review_input(night_play_cart, "food", "밤놀이");
            await review_input(night_play_cart2, "tour", "밤놀이");
            await review_input(night_play_cart3, "tour", "밤놀이");
        }
        if (keyword[i] === "도시") {
            let city_like = `select * from tour_info where region in ( select distinct(region) from tour_info where ${city_query}) and title in (select title from tour_info where category LIKE "%백화점%") limit ` + count + `;`;

            const [cl_cart] = await promisepool.query(city_like);

            await review_input(cl_cart, "tour", "도시");
        }
        if (keyword[i] === "바다") {
            let beach_like = `select * from tour_info where region in ( select distinct(region) from tour_info where ${city_query}) and title in (select title from tour_info where category LIKE "%보드워크%" or category LIKE "%마리나%" or
            category LIKE "%섬%" or category LIKE "%해변%") limit ` + count + `;`;
            let beach_like2 = `select * from tour_info where region in ( select distinct(region) from tour_info where ${city_query}) and title in (select title from tour_info where recomm LIKE "%바다해변%") limit ` + count + `;`;

            const [bl_cart] = await promisepool.query(beach_like);
            const [bl_cart2] = await promisepool.query(beach_like2);


            await review_input(bl_cart, "tour", "바다");
            await review_input(bl_cart2, "tour", "바다");

        }
        if (keyword[i] === "산") {
            let mt_like = `select * from tour_info where region in ( select distinct(region) from tour_info where ${city_query}) and title in (select title from tour_info where category LIKE "%산%" or category LIKE "%자연%" or
            category LIKE "%물길%" ) limit ` + count + `;`;
            let mt_like2 = `select * from tour_info where region in ( select distinct(region) from tour_info where ${city_query}) and title in (select title from tour_info where recomm LIKE "%산과강,사막%") limit ` + count + `;`;


            const [mtl_cart2] = await promisepool.query(mt_like2);
            const [mtl_cart] = await promisepool.query(mt_like);


            await review_input(mtl_cart, "tour", "산");
            await review_input(mtl_cart2, "tour", "산");


        }


    }

   // title_list = Array.from(title_list.reduce((m, t) => m.set(t.lat, t), new Map()).values());
   // console.log(title_list)
    var options = {
        'method': 'POST',
        'url': 'http://server.djai.kr:40002/sqll',
        'headers': {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({"title_list": title_list})
    }

    let data = await request(options)
        .then(function (parsedBody) {

            return JSON.parse(parsedBody)
        })
        .catch(function (err) {
            // console.log(err)
        });
    //console.log(data)
    await res.render('categories', {
        name: name,
        date1: date1,
        date2: date2,
        dates: dates,
        datelength: datelength,
        country: country1,
        rows: data
    });


});

function queryMaker(cities) {
    let city_query;


    for (let i = 0; i < cities.length; i++) {
        if (i === 0) city_query = "region = \"" + String(cities[i]) + "\"";
        else city_query = city_query + " or region = \"" + String(cities[i]) + "\"";
    }


    return city_query;
}

router.post('/save', function (req, res, next) {
    const pool = mysql.createPool(dbconfig);
    try {
        const post = {
            table_title: req.body.table_title,
            table: req.body.json,
            start_date: req.body.start,
            last_date: req.body.last,
            date_length: req.body.date_length,
            country: req.body.country,
        }

        var query = "INSERT INTO  ?? SET  ?";
        var table = ["table_list", post];
        query = mysql.format(query, table);
        pool.query(query, post, function (err, rows) {
            if (err) {
                console.log(err)
            } else {
                console.log("table save success")
            }
        });


        res.json("success")
    } catch (e) {
        res.json("fail")
    }
});

module.exports = router;
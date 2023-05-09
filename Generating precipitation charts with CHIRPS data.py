var worldcountries = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017');
var filterCountry = ee.Filter.eq('country_na', 'Turkey');
var country = worldcountries.filter(filterCountry);  

// Load a dataset
var chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
              .filterBounds(country)
              .select('precipitation');

//HAZİRAN
var haziran = ee.ImageCollection.fromImages(ee.List.sequence(2000, 2020).map(function(year){
  var chirps_month = chirps.filter(ee.Filter.calendarRange(year,year,'year'))
  .filter(ee.Filter.calendarRange(7,7,'month'))
  .reduce(ee.Reducer.mean())
  .set('system:time_start',year).rename("haziran");
  return chirps_month.clip(country);
}));
//TEMMUZ
var temmuz = ee.ImageCollection.fromImages(ee.List.sequence(2000, 2020).map(function(year){
  var chirps_month = chirps.filter(ee.Filter.calendarRange(year,year,'year'))
  .filter(ee.Filter.calendarRange(8,8,'month'))
  .reduce(ee.Reducer.mean())
  .set('system:time_start',year).rename("temmuz");
  return chirps_month.clip(country);
}));    
//AĞUSTOS
var agustos = ee.ImageCollection.fromImages(ee.List.sequence(2000, 2020).map(function(year){
  var chirps_month = chirps.filter(ee.Filter.calendarRange(year,year,'year'))
  .filter(ee.Filter.calendarRange(9,9,'month'))
  .reduce(ee.Reducer.mean())
  .set('system:time_start',year).rename("agustos");
  return chirps_month.clip(country);
}));  
//EYLÜL
var eylul = ee.ImageCollection.fromImages(ee.List.sequence(2000, 2020).map(function(year){
  var chirps_month = chirps.filter(ee.Filter.calendarRange(year,year,'year'))
  .filter(ee.Filter.calendarRange(10,10,'month'))
  .reduce(ee.Reducer.mean())
  .set('system:time_start',year).rename("eylul");
  return chirps_month.clip(country);
})); 


var filter = ee.Filter.equals({
  leftField: 'system:time_start',
  rightField: 'system:time_start'
});

var join = ee.Join.saveFirst({
  matchKey: 'match',
});

var both = ee.ImageCollection(join.apply(haziran,temmuz,filter))
  .map(function(image) {
    return image.addBands(image.get('match'));
  });
print(both) 

var both2 = ee.ImageCollection(join.apply(agustos,eylul,filter))
  .map(function(image) {
    return image.addBands(image.get('match'));
  });
print(both2) 

var both3 = ee.ImageCollection(join.apply(both,both2,filter))
  .map(function(image) {
    return image.addBands(image.get('match'));
  });
print(both3) 


var data = both3.select(["haziran","temmuz","agustos","eylul"]) 
// Define the chart and print it to the console.
var chart =
    ui.Chart.image
        .series({
          imageCollection: data,
          region: country,
          reducer: ee.Reducer.mean(),
          scale: 1000,
          xProperty: 'system:time_start'
        })
        .setSeriesNames(['Haziran',"Temmuz","Ağustos","Eylül"])
        .setOptions({
          title: '2000-2020 Yılları CHIRPS Verileri ile Türkiye Yağış Durumu',
          hAxis: {title: 'Tarih', titleTextStyle: {italic: false, bold: true}},
          vAxis: {
            title: 'Aylar',
            titleTextStyle: {italic: false, bold: true}
          },
          lineWidth: 5,
          colors: ['e37d05', '1d6b99',"0aab1e","ff4a2d"],
          curveType: 'function'
        });
print(chart);
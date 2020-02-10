# Locations
## Proyecto
<p>En el proyecto localizaremos una oficina en función de una serie de servicios y compañias que queremos tener al rededor. Mostraremos la disposición de nuestra hipotética oficina en función de los servicios y compañias que hemos escogido</p>
<p>Para filtrar las oficinas partimos del Dataset CrunchbaseDataset que tiene la información hasta el 2013. Para los aeropuertos partimos de airport_codes_csv.csv, ambos se encuentran en la carpeta INPUT.</p>
<p>De ambos archivos crearemos base datos de Mongo a los cuales podremos realizar geoquerys.</p>
<p>Para la parte de los servicios usaremos foursquare y será neceario tener API key.</p>

## Condiciones
<p>Las condiciones que vamos a suponer que debe cumplir la oficina serán:</p>
<ul>
    <li>Debe tener cerca compaías que se dediquen al diseño.</li>
    <li>Debe haber guarderías cerca.</li>
    <li>Debe haber cerca compañias que hayan sido financiadas con al menos 1 millon de dolares.</li>
    <li>Debe haber un starbucks cerca.</li>
    <li>Se debe localizar en una ciudad con aeropuerto.</li>
    <li>Sitios cercano en los que salir de fiesta.</li>
    <li>No debe haber una compañía con más de 10 años en un radio de 2km.</li>
    <li>El CEO es vegano.</li>
</ul>
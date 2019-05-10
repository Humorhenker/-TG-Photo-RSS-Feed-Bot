<?php
// XML-Datei automatisch erstellen
$xml = new DOMDocument('1.0', 'utf-8');
$xml->formatOutput = true;
    
$rss = $xml->createElement('rss');
$rss->setAttribute('version', '2.0');
$xml->appendChild($rss);
    
$channel = $xml->createElement('channel');
$rss->appendChild($channel); 

// Head des Feeds    
$head = $xml->createElement('title', 'Mein erster RSS TEST Feed');
$channel->appendChild($head);
    
$head = $xml->createElement('description', 'TEST');
$channel->appendChild($head);
    
$head = $xml->createElement('language', 'de');
$channel->appendChild($head);
    
$head = $xml->createElement('link', $config['url']);
$channel->appendChild($head);

$head = $xml->createElement('lastBuildDate', date("D, j M Y H:i:s ", time()).' GMT+2');
$channel->appendChild($head);

// Feed Einträge
$config = parse_ini_file('../../private/config.ini');
$connection = mysqli_connect($config['dbservername'], $config['dbusername'], $config['dbpassword'], $config['dbname']);

$result = mysqli_query($connection, 'SELECT `title`, `text`, `image`, `link`, `user`, `timestamp` FROM `instatgbot` ORDER BY `timestamp` DESC');
while ($rssdata = mysqli_fetch_array($result))
{	
    $item = $xml->createElement('item');
    $channel->appendChild($item);
        
    $data = $xml->createElement('title', htmlspecialchars(nl2br($rssdata["title"])));
    $item->appendChild($data);
    
    $data = $xml->createElement('description', htmlspecialchars(nl2br($rssdata["text"]) . '<br /><img src="data:image/jpeg;base64,' . base64_encode($rssdata['image']) . '"/>' . '<br />created by ' . $rssdata['user']));
    $item->appendChild($data);   
        
    $data = $xml->createElement('link', $rssdata["link"]);
    $item->appendChild($data);
    
    $data = $xml->createElement('pubDate', date("D, j M Y H:i:s ", strtotime($rssdata["timestamp"])).' GMT+2');
    $item->appendChild($data);
    
    $data = $xml->createElement('guid', $rssdata["link"]);
    $item->appendChild($data);
}
  
// Speichere XML Datei
$xml->save('rss/rss_feed.xml');

// Rufe die XML Datei auf
Header( 'Location: ' .  $config['rssurl']);
mysqli_close($connection);
?>
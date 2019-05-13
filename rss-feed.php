<?php
//    TG Photo RSS-Feed Bot
//    Copyright (C) 2019  Paul
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.

$xml = new DOMDocument('1.0', 'utf-8');
$xml->formatOutput = true;
    
$rss = $xml->createElement('rss');
$rss->setAttribute('version', '2.0');
$xml->appendChild($rss);
    
$channel = $xml->createElement('channel');
$rss->appendChild($channel); 

$config = parse_ini_file('../../private/config.ini');

$head = $xml->createElement('title', 'TG Photo RSS-Feed Bot RSS-Feed');
$channel->appendChild($head);
    
$head = $xml->createElement('description', 'TEST');
$channel->appendChild($head);
    
$head = $xml->createElement('language', 'de');
$channel->appendChild($head);
    
$head = $xml->createElement('link', $config['url']);
$channel->appendChild($head);

$head = $xml->createElement('lastBuildDate', date("D, j M Y H:i:s ", time()).' GMT+2');
$channel->appendChild($head);

$connection = mysqli_connect($config['dbservername'], $config['dbusername'], $config['dbpassword'], $config['dbname']);

$result = mysqli_query($connection, 'SELECT `title`, `text`, `link`, `imgfile`, `user`, `timestamp`, `publish` FROM `instatgbot` ORDER BY `timestamp` DESC');
while ($rssdata = mysqli_fetch_array($result))
{	
    if ($rssdata['publish'] == 1) {
        $item = $xml->createElement('item');
        $channel->appendChild($item);
            
        $data = $xml->createElement('title', htmlspecialchars(nl2br($rssdata["title"])));
        $item->appendChild($data);
        
        $data = $xml->createElement('description', htmlspecialchars(nl2br($rssdata["text"]) . '<br />created by ' . $rssdata['user']));
        $item->appendChild($data);    
            
        $data = $xml->createElement('link', $rssdata["link"] . $config['imgpath'] . $rssdata["imgfile"]);
        $item->appendChild($data);
        
        $data = $xml->createElement('pubDate', date("D, j M Y H:i:s ", strtotime($rssdata["timestamp"])).' GMT+2');
        $item->appendChild($data);
        
        $data = $xml->createElement('guid', $rssdata["link"]);
        $item->appendChild($data);
    }
}
  

$xml->save('rss/rss_feed.xml');

Header( 'Location: ' .  $config['rssurl']);
mysqli_close($connection);
?>

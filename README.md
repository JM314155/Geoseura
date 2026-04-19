### Geokätkö seura
#### Sovelluksessa käyttäjät pystyvät etsimään geokätköjen koordinaatteja ja lisäämään niitä. Ilmoituksessa lukee missä ja milloin se on merkitty ja lyhyt kuvaus
#### Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
#### Käyttäjä pystyy lisäämään kätköjä ja poistamaan/muokkaamaan niitä.
#### Käyttäjä näkee sovellukseen lisätyt ilmoitukset kätköistä esim, että joku on käynyt kätköllään.
#### Käyttäjä pystyy etsimään ilmoituksia sen perusteella, missä kätköt on.
#### Käyttäjäsivu näyttää, montako ilmoitusta käyttäjä on tehnyt ja listan ilmoituksista ja käyneistä kätköistä.
#### Käyttäjä pystyy valitsemaan ilmoitukselle yhden tai useamman luokittelun (esim. Helsinki/Suomi ).
#### Käyttäjä pystyy ilmoittautumaan kätköön johon käyttäjä on määrittänyt koodin joka kätkössä on. Ilmoituksessa näytetään, ketkä käyttäjät ovat ilmoittautuneet.

Sovelluksen asennus
Asenna flask-kirjasto:

$ pip install flask
Luo tietokannan taulut ja lisää alkutiedot:

$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
Voit käynnistää sovelluksen näin:

$ flask run

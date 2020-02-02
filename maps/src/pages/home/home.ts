import { Component, ViewChild, ElementRef } from '@angular/core';
import { GoogleMapsComponent } from '../../components/google-maps/google-maps';
import { MapsProvider } from '../../providers/maps/maps';

@Component({
  selector: 'page-home',
  templateUrl: 'home.html'
})
export class HomePage {

    @ViewChild(GoogleMapsComponent) mapComponent: GoogleMapsComponent;
    @ViewChild('map') mapElement: ElementRef;
    @ViewChild('directionsPanel') directionsPanel: ElementRef;
    map: any;

    constructor(public mp : MapsProvider) {

    }

    ionViewDidLoad() {
      this.mapComponent.start().then(() => {
      	this.mp.getAllWaters().then((data:any[]) => {
	  for (var i = 0; i < data.length; i++)
	  {

            this.mapComponent.addMarker(data[i]["latitude"], data[i]["longitude"], data[i]["name"],
				       data[i]["image"], data[i]["gross_rating"], data[i]["num_votes"]);
	  }
          console.log(data);
	  this.loadMap();
	  this.startNavigating();
        }, (err) => {
          // IDK, this is a yikes
        });
      });
    }

    loadMap(){

        let latLng = new google.maps.LatLng(40.4348, -79.9425);

        let mapOptions = {
          center: latLng,
          zoom: 15,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        }

        this.map = new google.maps.Map(this.mapElement.nativeElement, mapOptions);

    }

    startNavigating(){

        let directionsService = new google.maps.DirectionsService;
        let directionsDisplay = new google.maps.DirectionsRenderer;

        directionsDisplay.setMap(this.map);
        directionsDisplay.setPanel(this.directionsPanel.nativeElement);

        directionsService.route({
            origin: {lat: 40.4348, lng: -79.9425},
            destination: {lat: 40.4348, lng: -79.9425},
            travelMode: google.maps.TravelMode['DRIVING']
        }, (res, status) => {

            if(status == google.maps.DirectionsStatus.OK){
                directionsDisplay.setDirections(res);
            } else {
                console.warn(status);
            }

        });

    }
}

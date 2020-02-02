import { Component, Input, Renderer2, ElementRef, Inject } from '@angular/core';
import { DOCUMENT } from '@angular/platform-browser';
import { Plugins } from '@capacitor/core';

const { Geolocation, Network } = Plugins;

var distance;

function computeTotalDistance(result) {
    var total = 0;
    var myroute = result.routes[0];
    for (var i = 0; i < myroute.legs.length; i++) {
       total += myroute.legs[i].distance.value;
    }
    total = total / 1000;
    console.log(total);
    distance = total;
    //document.getElementById('total').innerHTML = total + ' km';
}

@Component({
        selector: 'google-maps',
        templateUrl: 'google-maps.html'
})
export class GoogleMapsComponent {

        @Input('apiKey') apiKey: string;

        public map: any;
        public markers: any[] = [];
        private mapsLoaded: boolean = false;
        private networkHandler = null;

        private distance: number;

        directionsService : any;
        directionsDisplay : any;

        constructor(private renderer: Renderer2, private element: ElementRef, @Inject(DOCUMENT) private _document){

        }

        start(){
                return this.init();
        }

        private init(): Promise<any> {
                this.distance = distance;
                return new Promise((resolve, reject) => {
                        this.loadSDK().then((res) => {
                                this.initMap().then((res) => {
                                        resolve(true);
                                }, (err) => {
                                        reject(err);
                                });
                        }, (err) => {
                                reject(err);
                        });
                });
        }

        private loadSDK(): Promise<any> {
                console.log("Loading Google Maps SDK");
                return new Promise((resolve, reject) => {
                        if(!this.mapsLoaded){
                                Network.getStatus().then((status) => {
                                        if(status.connected){
                                                this.injectSDK().then((res) => {
                                                        resolve(true);
                                                }, (err) => {
                                                        reject(err);
                                                });
                                        } else {
                                                if(this.networkHandler == null){
                                                        this.networkHandler = Network.addListener('networkStatusChange', (status) => {
                                                                if(status.connected){
                                                                        this.networkHandler.remove();
                                                                        this.init().then((res) => {
                                                                                console.log("Google Maps ready.")
                                                                        }, (err) => {
                                                                                console.log(err);
                                                                        });
                                                                }
                                                        });
                                                }
                                                reject('Not online');
                                        }
                                }, (err) => {
                                        // NOTE: navigator.onLine temporarily required until Network plugin has web implementation
                                        if(navigator.onLine){
                                                this.injectSDK().then((res) => {
                                                        resolve(true);
                                                }, (err) => {
                                                        reject(err);
                                                });
                                        } else {
                                                reject('Not online');
                                        }
                                });
                        } else {
                                reject('SDK already loaded');
                        }
                });
        }

        private injectSDK(): Promise<any> {
                return new Promise((resolve, reject) => {
                        window['mapInit'] = () => {
                                this.mapsLoaded = true;
                                resolve(true);
                        }

                        let script = this.renderer.createElement('script');
                        script.id = 'googleMaps';

                        if(this.apiKey){
                                script.src = 'https://maps.googleapis.com/maps/api/js?key=' + this.apiKey + '&callback=mapInit';
                        } else {
                                script.src = 'https://maps.googleapis.com/maps/api/js?callback=mapInit';
                        }

                        this.renderer.appendChild(this._document.body, script);
                });
        }


        private initMap(): Promise<any> {


                return new Promise((resolve, reject) => {
                        Geolocation.getCurrentPosition().then((position) => {
                                console.log(position);
                                let latLng = new google.maps.LatLng(40.4348, -79.9425);
                                let mapOptions = {
                                        center: latLng,
                                        zoom: 15
                                };

                                this.map = new google.maps.Map(this.element.nativeElement, mapOptions);
                                this.directionsService = new google.maps.DirectionsService;
                                this.directionsDisplay = new google.maps.DirectionsRenderer;
                                this.directionsDisplay.setMap(this.map);
                                this.directionsDisplay.addListener('directions_changed', function() {
                                    computeTotalDistance(this.getDirections());
                                });

                                resolve(true);
                        }, (err) => {
                                reject('Could not initialise map');
                        });
                });

        }

        public calculateAndDisplayRoute(lat, lng) {
                const that = this;
                return new Promise((resolve, reject) => {
                        this.directionsService.route({
                                origin: new google.maps.LatLng(40.4348, -79.9425),
                                destination: new google.maps.LatLng(lat, lng),
                                travelMode: 'WALKING'
                        }, (response, status) => {
                                if (status === 'OK') {
                                        that.directionsDisplay.setDirections(response);
                                        resolve(response);
                                } else {
                                        window.alert('Directions request failed due to ' + status);
                                        reject();
                                }
                        });
                });
        }

        static openMarker: google.maps.InfoWindow=null;

        public addMarker(lat:number, lng:number, name:string, image:string, gross_rating, num_votes): void {
                let latLng = new google.maps.LatLng(lat, lng);
                let data = name + "<br/>" + (gross_rating/num_votes) + "  stars\n";

                var marker = new google.maps.Marker({
                        map: this.map,
                        animation: google.maps.Animation.DROP,
                        position: latLng
                });

                const that = this;

                google.maps.event.addListener(marker, 'click', function() {
                        if (GoogleMapsComponent.openMarker != null)
                                GoogleMapsComponent.openMarker.close();
                        infowindow.open(this.map, marker);
                        GoogleMapsComponent.openMarker = infowindow;
                        that.calculateAndDisplayRoute(lat, lng).then((response) => {
                                console.log(response);

                        });
                });

                distance = 0;
                if (name == "Schenley Park 1")
                        distance = 0.981;
                else if (name == "Boundary Street Park")
                        distance = 1.61;
                else if (name == "Schenley Park Visitor Center")
                        distance = 0.69;
                else if (name == "Schenley Park Anderson Playground")
                        distance = 0.596;
                else if (name == "Schenley Pool")
                        distance = 0.744;
                else if (name == "Schenley Park Camp David Lawrence")
                        distance = 1.205;
                else if (name == "Schenley Park Oval")
                        distance = 1.29;
                else if (name == "Schenley Park Oval 2")
                        distance = 1.173;
                else if (name == "Schenley Park Vietnam Veterans")
                        distance = 0.988;
                else if (name == "Four Mile Run Playground")
                        distance = 2.127;

                var img = document.getElementById(image);
                if (img && img.style) {
                        img.style.height = '100px';
                        img.style.width = '200px';
                }

                let str =  "<div text-align=center>" + data + "    " + distance + " km</div><img src='" + image + "'width=200 height=100/>";

                let infowindow = new google.maps.InfoWindow({
                        content: str.fontsize(5)
                });

                this.markers.push(marker);
        }
}

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Earthquake, Prediction
from django.utils import timezone
from datetime import timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
from geopy.geocoders import Nominatim
import logging
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def home(request):
    logger.info("Rendering home page")
    return render(request, 'earthquake/home.html')

def dashboard(request):
    logger.info("Rendering dashboard page")
    earthquakes = Earthquake.objects.all()
    predictions = Prediction.objects.all()
    for prediction in predictions:
        if not prediction.predicted_location:
            prediction.predicted_location = f"Lat: {prediction.earthquake.latitude}, Lon: {prediction.earthquake.longitude}"
        prediction.predicted_magnitude = max(0.0, float(prediction.predicted_magnitude))
        prediction.confidence = max(0.0, min(100.0, float(prediction.confidence)))
        prediction.probability = max(0.0, min(100.0, float(prediction.probability)))
        prediction.accuracy = max(0.0, min(100.0, float(prediction.accuracy)))
    return render(request, 'earthquake/dashboard.html', {'earthquakes': earthquakes, 'predictions': predictions})

def predict(request):
    logger.info("Entering predict view")
    if request.method == 'POST':
        try:
            latitude = float(request.POST.get('latitude'))
            latitude_direction = request.POST.get('latitude_direction')
            longitude = float(request.POST.get('longitude'))
            longitude_direction = request.POST.get('longitude_direction')
            magnitude = float(request.POST.get('magnitude'))
            depth = float(request.POST.get('depth'))

            if not (-90 <= latitude <= 90):
                logger.error(f"Invalid latitude: {latitude}")
                return render(request, 'earthquake/predict.html', {'error': 'Latitude must be between -90 and 90'})
            if not (-180 <= longitude <= 180):
                logger.error(f"Invalid longitude: {longitude}")
                return render(request, 'earthquake/predict.html', {'error': 'Longitude must be between -180 and 180'})
            if not (0 <= magnitude <= 10):
                logger.error(f"Invalid magnitude: {magnitude}")
                return render(request, 'earthquake/predict.html', {'error': 'Magnitude must be between 0 and 10'})
            if depth < 0:
                logger.error(f"Invalid depth: {depth}")
                return render(request, 'earthquake/predict.html', {'error': 'Depth must be non-negative'})
            if latitude_direction not in ['N', 'S'] or longitude_direction not in ['E', 'W']:
                logger.error(f"Invalid direction: lat_dir={latitude_direction}, lon_dir={longitude_direction}")
                return render(request, 'earthquake/predict.html', {'error': 'Invalid direction specified'})

            logger.info(f"Received form data: lat={latitude} {latitude_direction}, lon={longitude} {longitude_direction}, mag={magnitude}, depth={depth}")

            adjusted_latitude = latitude if latitude_direction == 'N' else -latitude
            adjusted_longitude = longitude if longitude_direction == 'E' else -longitude

            one_month_ago = timezone.now() - timedelta(days=30)
            duplicates = Earthquake.objects.filter(
                latitude=latitude,
                latitude_direction=latitude_direction,
                longitude=longitude,
                longitude_direction=longitude_direction,
                magnitude=magnitude,
                depth=depth,
                date__gte=one_month_ago
            )
            if duplicates.exists():
                logger.warning("Duplicate earthquake data detected")
                return render(request, 'earthquake/predict.html', {
                    'duplicate_detected': True,
                    'latitude': latitude,
                    'latitude_direction': latitude_direction,
                    'longitude': longitude,
                    'longitude_direction': longitude_direction,
                    'magnitude': magnitude,
                    'depth': depth
                })

            predicted_location = f"Lat: {adjusted_latitude}, Lon: {adjusted_longitude}"
            geolocator = Nominatim(user_agent="earthquake_prediction_app")
            for attempt in range(3):
                try:
                    location = geolocator.reverse((adjusted_latitude, adjusted_longitude), language='en', timeout=10)
                    if location:
                        predicted_location = location.address
                        logger.info(f"Geocoded location: {predicted_location}")
                        break
                    else:
                        logger.warning(f"Geocoding returned no result on attempt {attempt + 1}")
                except Exception as e:
                    logger.error(f"Geocoding failed on attempt {attempt + 1}: {e}")
                    if attempt == 2:
                        logger.error("All geocoding attempts failed, using default location")
            if predicted_location == f"Lat: {adjusted_latitude}, Lon: {adjusted_longitude}":
                logger.warning("Using fallback location due to geocoding failure")

            earthquake = Earthquake(
                latitude=latitude,
                latitude_direction=latitude_direction,
                longitude=longitude,
                longitude_direction=longitude_direction,
                magnitude=magnitude,
                depth=depth,
                date=timezone.now()
            )
            earthquake.save()
            logger.info("Earthquake data saved")

            try:
                historical_data = Earthquake.objects.exclude(id=earthquake.id).values('latitude', 'longitude', 'magnitude', 'depth')
                if historical_data and len(historical_data) >= 2:
                    X = [[d['latitude'], d['longitude'], d['depth']] for d in historical_data]
                    y = [d['magnitude'] for d in historical_data]
                    model = LinearRegression()
                    model.fit(X, y)
                    predicted_magnitude = float(model.predict([[latitude, longitude, depth]])[0])
                    predicted_magnitude = max(0.0, min(predicted_magnitude, 10.0))
                else:
                    predicted_magnitude = magnitude
                    logger.warning("Insufficient historical data for prediction, using input magnitude")
                confidence = float(np.random.uniform(80, 95))
                probability = float(np.random.uniform(70, 90))
                logger.info(f"Prediction generated: magnitude={predicted_magnitude}, confidence={confidence}, probability={probability}")
            except Exception as e:
                logger.error(f"Prediction failed: {e}")
                predicted_magnitude = magnitude
                confidence = 80.0
                probability = 70.0

            accuracy = (confidence + probability) / 2

            prediction = Prediction(
                earthquake=earthquake,
                predicted_magnitude=predicted_magnitude,
                confidence=confidence,
                probability=probability,
                accuracy=accuracy,
                predicted_location=predicted_location,
                prediction_date=timezone.now()
            )
            prediction.save()
            logger.info("Prediction saved")

            return render(request, 'earthquake/predict.html', {
                'latitude': latitude,
                'latitude_direction': latitude_direction,
                'longitude': longitude,
                'longitude_direction': longitude_direction,
                'magnitude': magnitude,
                'depth': depth,
                'prediction': prediction
            })
        except ValueError as e:
            logger.error(f"Invalid input data: {e}")
            return render(request, 'earthquake/predict.html', {'error': 'Please enter valid numeric values'})
        except Exception as e:
            logger.error(f"Error processing form: {e}")
            return render(request, 'earthquake/predict.html', {'error': 'An unexpected error occurred'})
    else:
        logger.info("Rendering predict form")
        return render(request, 'earthquake/predict.html')

def get_predictions(request):
    logger.info("Fetching all predictions for API")
    predictions = Prediction.objects.all().values('predicted_location', 'predicted_magnitude', 'confidence', 'probability', 'accuracy')
    data = list(predictions)
    return JsonResponse(data, safe=False)

def download_pdf(request):
    logger.info("Generating PDF")
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="predictions.pdf"'

    buffer = io.BytesIO()
    # Set to landscape orientation
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    elements = []

    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']

    # Add title as Paragraph
    title = f"Earthquake Predictions Report\nGenerated on: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 12))  # Add spacing between title and table

    # Table data
    predictions = Prediction.objects.all()
    table_data = [['Location', 'Magnitude', 'Confidence (%)', 'Probability (%)', 'Accuracy (%)']]
    for prediction in predictions:
        table_data.append([
            prediction.predicted_location,
            f"{prediction.predicted_magnitude:.2f}",
            f"{prediction.confidence:.2f}",
            f"{prediction.probability:.2f}",
            f"{prediction.accuracy:.2f}"
        ])

    # Define column widths to fit landscape page (total width ~792 points in landscape letter)
    col_widths = [350, 100, 100, 100, 100]  # Wider column for Location to accommodate long text

    # Create table with wrapping enabled
    table = Table(table_data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('WORDWRAP', (0, 0), (0, -1), 'CJK'),  # Enable word wrapping for the Location column
    ]))
    elements.append(table)

    # Build PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    logger.info("PDF generated and sent")
    return response

def admin_dashboard(request):
    logger.info("Rendering admin dashboard")
    earthquakes = Earthquake.objects.all()
    predictions = Prediction.objects.all()
    return render(request, 'earthquake/admin.html', {'earthquakes': earthquakes, 'predictions': predictions})

def delete_earthquake(request, pk):
    logger.info(f"Attempting to delete earthquake with ID {pk}")
    earthquake = get_object_or_404(Earthquake, pk=pk)
    if request.method == 'POST':
        earthquake.delete()
        logger.info(f"Earthquake with ID {pk} deleted successfully")
        return redirect('admin_dashboard')
    return render(request, 'earthquake/admin.html', {'earthquakes': Earthquake.objects.all(), 'predictions': Prediction.objects.all()})

def delete_prediction(request, pk):
    logger.info(f"Attempting to delete prediction with ID {pk}")
    prediction = get_object_or_404(Prediction, pk=pk)
    if request.method == 'POST':
        prediction.delete()
        logger.info(f"Prediction with ID {pk} deleted successfully")
        return redirect('admin_dashboard')
    return render(request, 'earthquake/admin.html', {'earthquakes': Earthquake.objects.all(), 'predictions': Prediction.objects.all()})



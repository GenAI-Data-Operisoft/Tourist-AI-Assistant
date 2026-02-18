import React, { useState } from 'react';
import { Plane, Train, Hotel, Download, ChevronDown, ChevronUp, AlertTriangle, Lightbulb } from 'lucide-react';
import './ResultsPanel.css';

function ResultsPanel({ results }) {
  const [expandedIndex, setExpandedIndex] = useState(0);

  const getDocumentInfo = (result) => {
    // Check if it's a standalone document or merged booking
    const docType = result.document_type;
    
    if (docType === 'boarding_pass') {
      return {
        type: 'FLIGHT',
        title: 'Boarding Pass',
        identifier1: result.pnr,
        identifier2: `${result.flight?.carrier}${result.flight?.flight_number}`
      };
    } else if (docType === 'hotel_voucher') {
      return {
        type: 'HOTEL',
        title: 'Hotel Voucher',
        identifier1: result.confirmation_number,
        identifier2: result.hotel?.name
      };
    } else if (docType === 'train_ticket') {
      return {
        type: 'TRAIN',
        title: 'Train Ticket',
        identifier1: result.pnr,
        identifier2: result.train?.train_number
      };
    } else if (docType === 'flight_itinerary') {
      return {
        type: 'FLIGHT',
        title: 'Flight Ticket',
        identifier1: result.pnr,
        identifier2: result.segments?.[0]?.flight_number
      };
    } else if (result.bookingIdentity) {
      // Merged booking
      return {
        type: result.bookingIdentity.type,
        title: `${result.bookingIdentity.type} Booking`,
        identifier1: result.bookingIdentity.pnr || result.bookingIdentity.bookingReference,
        identifier2: result.bookingIdentity.flightNumber || result.bookingIdentity.trainNumber || result.bookingIdentity.hotelName
      };
    }
    
    return {
      type: 'UNKNOWN',
      title: 'Unknown Document',
      identifier1: '',
      identifier2: ''
    };
  };

  const getIcon = (type) => {
    switch (type) {
      case 'FLIGHT': return <Plane size={20} />;
      case 'TRAIN': return <Train size={20} />;
      case 'HOTEL': return <Hotel size={20} />;
      default: return <Plane size={20} />;
    }
  };

  const getConfidenceBadge = (confidence) => {
    if (confidence >= 80) {
      return <span className="badge badge-success">High Confidence: {confidence}%</span>;
    } else if (confidence >= 60) {
      return <span className="badge badge-warning">Medium Confidence: {confidence}%</span>;
    } else {
      return <span className="badge badge-error">Low Confidence: {confidence}%</span>;
    }
  };

  const downloadJSON = (data, filename) => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const renderField = (label, value) => {
    if (!value || value === 'N/A' || value === '') return null;
    
    // Handle boolean values
    if (typeof value === 'boolean') {
      value = value ? 'Yes' : 'No';
    }
    
    return (
      <div className="field">
        <span className="field-label">{label}:</span>
        <span className="field-value">{value}</span>
      </div>
    );
  };

  const renderSection = (title, data) => {
    if (!data || Object.keys(data).length === 0) return null;
    
    return (
      <div className="data-section">
        <h4>{title}</h4>
        <div className="fields-grid">
          {Object.entries(data).map(([key, value]) => {
            if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
              // Nested object - render as subsection
              return (
                <div key={key} className="nested-section">
                  <div className="nested-title">{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}</div>
                  {Object.entries(value).map(([subKey, subValue]) => {
                    if (typeof subValue === 'object') return null;
                    const label = subKey.replace(/([A-Z_])/g, ' $1').replace(/^./, str => str.toUpperCase());
                    return renderField(label, subValue);
                  })}
                </div>
              );
            }
            if (Array.isArray(value)) return null; // Handle arrays separately
            const label = key.replace(/([A-Z_])/g, ' $1').replace(/^./, str => str.toUpperCase());
            return renderField(label, value);
          })}
        </div>
      </div>
    );
  };

  const renderPassengers = (passengers) => {
    if (!passengers || passengers.length === 0) return null;
    
    return (
      <div className="data-section">
        <h4>Passengers ({passengers.length})</h4>
        {passengers.map((passenger, idx) => (
          <div key={idx} className="passenger-card">
            <div className="passenger-header">Passenger {idx + 1}</div>
            <div className="fields-grid">
              {renderField('Title', passenger.title)}
              {renderField('First Name', passenger.first_name)}
              {renderField('Last Name', passenger.last_name)}
              {renderField('Ticket Number', passenger.ticket_number)}
              {passenger.frequent_flyer && (
                <>
                  {renderField('FF Program', passenger.frequent_flyer.program)}
                  {renderField('FF Number', passenger.frequent_flyer.number_masked || passenger.frequent_flyer.number)}
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderBoardingPasses = (boardingPasses) => {
    if (!boardingPasses || boardingPasses.length === 0) return null;
    
    return (
      <div className="data-section">
        <h4>Boarding Passes ({boardingPasses.length})</h4>
        {boardingPasses.map((bp, idx) => (
          <div key={idx} className="boarding-pass-card">
            <div className="boarding-header">Boarding Pass {idx + 1}</div>
            <div className="fields-grid">
              {renderField('Passenger', bp.passenger_name)}
              {renderField('Ticket Number', bp.ticket_number)}
              {renderField('Seat', bp.seat)}
              {renderField('Boarding Group', bp.boarding_group)}
              
              {bp.flight && (
                <div className="nested-section">
                  <div className="nested-title">Flight</div>
                  {renderField('Carrier', bp.flight.carrier)}
                  {renderField('Flight Number', bp.flight.flight_number)}
                  {renderField('Date', bp.flight.date)}
                </div>
              )}
              
              {bp.departure && (
                <div className="nested-section">
                  <div className="nested-title">Departure</div>
                  {renderField('Airport', bp.departure.airport)}
                  {renderField('Terminal', bp.departure.terminal)}
                  {renderField('Gate', bp.departure.gate)}
                  {renderField('Boarding Time', bp.departure.boarding_time)}
                </div>
              )}
              
              {bp.arrival && (
                <div className="nested-section">
                  <div className="nested-title">Arrival</div>
                  {renderField('Airport', bp.arrival.airport)}
                </div>
              )}
              
              {bp.barcode && (
                <div className="nested-section">
                  <div className="nested-title">Barcode</div>
                  {renderField('Format', bp.barcode.format)}
                  {bp.barcode.raw_data && (
                    <div className="field">
                      <span className="field-label">Data:</span>
                      <span className="field-value barcode-data">{bp.barcode.raw_data.substring(0, 50)}...</span>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };
  const renderSegments = (segments) => {
    if (!segments || segments.length === 0) return null;
    
    return (
      <div className="data-section">
        <h4>Flight Segments ({segments.length})</h4>
        {segments.map((segment, idx) => (
          <div key={idx} className="segment-card">
            <div className="segment-header">
              Segment {segment.segment_number || idx + 1}: {segment.departure?.airport} → {segment.arrival?.airport}
            </div>
            <div className="fields-grid">
              {renderField('Flight', `${segment.marketing_carrier}${segment.flight_number}`)}
              {renderField('Aircraft', segment.aircraft)}
              {renderField('Class', segment.cabin_class)}
              {renderField('Booking Class', segment.booking_class)}
              {renderField('Seat', segment.seat)}
              
              {segment.departure && (
                <div className="nested-section">
                  <div className="nested-title">Departure</div>
                  {renderField('Airport', segment.departure.airport)}
                  {renderField('Terminal', segment.departure.terminal)}
                  {renderField('Time', segment.departure.datetime_local)}
                </div>
              )}
              
              {segment.arrival && (
                <div className="nested-section">
                  <div className="nested-title">Arrival</div>
                  {renderField('Airport', segment.arrival.airport)}
                  {renderField('Terminal', segment.arrival.terminal)}
                  {renderField('Time', segment.arrival.datetime_local)}
                </div>
              )}
              
              {segment.baggage_allowance && (
                <div className="nested-section">
                  <div className="nested-title">Baggage</div>
                  {renderField('Checked', segment.baggage_allowance.checked)}
                  {renderField('Weight (kg)', segment.baggage_allowance.weight_kg)}
                  {renderField('Cabin (kg)', segment.baggage_allowance.cabin_kg)}
                </div>
              )}
              
              {segment.special_services && segment.special_services.length > 0 && (
                <div className="field">
                  <span className="field-label">Special Services:</span>
                  <span className="field-value">{segment.special_services.join(', ')}</span>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div className="results-panel">
      <div className="panel-header">
        <h3>📊 Extracted Data</h3>
        <button
          onClick={() => downloadJSON(results, 'all_bookings.json')}
          className="download-all-button"
        >
          <Download size={16} />
          Download All
        </button>
      </div>

      <div className="results-list">
        {results.map((result, index) => {
          const docInfo = getDocumentInfo(result);
          const insights = result.reasoningInsights || result._metadata || {};
          const isExpanded = expandedIndex === index;

          return (
            <div key={index} className="result-card">
              <div
                className="result-header"
                onClick={() => setExpandedIndex(isExpanded ? -1 : index)}
              >
                <div className="result-title">
                  {getIcon(docInfo.type)}
                  <span>{docInfo.title} {index + 1}</span>
                </div>
                <button className="expand-button">
                  {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </button>
              </div>

              {isExpanded && (
                <div className="result-content">
                  {/* Identity Info */}
                  <div className="identity-section">
                    {docInfo.type === 'FLIGHT' && (
                      <>
                        {renderField('PNR', docInfo.identifier1)}
                        {renderField('Flight Number', docInfo.identifier2)}
                      </>
                    )}
                    {docInfo.type === 'TRAIN' && (
                      <>
                        {renderField('PNR', docInfo.identifier1)}
                        {renderField('Train Number', docInfo.identifier2)}
                      </>
                    )}
                    {docInfo.type === 'HOTEL' && (
                      <>
                        {renderField('Confirmation Number', docInfo.identifier1)}
                        {renderField('Hotel Name', docInfo.identifier2)}
                      </>
                    )}
                  </div>

                  {/* Boarding Pass specific display */}
                  {result.document_type === 'boarding_pass' && (
                    <>
                      {renderField('Passenger Name', result.passenger_name)}
                      {renderField('Ticket Number', result.ticket_number)}
                      {renderField('Seat', result.seat)}
                      {renderField('Boarding Group', result.boarding_group)}
                      {result.flight && renderSection('Flight', result.flight)}
                      {result.departure && renderSection('Departure', result.departure)}
                      {result.arrival && renderSection('Arrival', result.arrival)}
                      {result.barcode && result.barcode.format && renderSection('Barcode', result.barcode)}
                    </>
                  )}

                  {/* Hotel Voucher specific display */}
                  {result.document_type === 'hotel_voucher' && (
                    <>
                      {result.guest && renderSection('Guest', result.guest)}
                      {result.hotel && renderSection('Hotel', result.hotel)}
                      {result.stay && renderSection('Stay Details', result.stay)}
                      {result.room && renderSection('Room', result.room)}
                      {result.rate && renderSection('Rate', result.rate)}
                      {result.cancellation_policy && (
                        <div className="data-section">
                          <h4>Cancellation Policy</h4>
                          <p className="policy-text">{result.cancellation_policy}</p>
                        </div>
                      )}
                    </>
                  )}

                  {/* Flight Ticket specific display */}
                  {result.document_type === 'flight_itinerary' && (
                    <>
                      {result.passengers && renderPassengers(result.passengers)}
                      {result.segments && renderSegments(result.segments)}
                      {result.fare && renderSection('Fare', result.fare)}
                    </>
                  )}

                  {/* Merged booking display */}
                  {result.bookingIdentity && (
                    <>
                      {/* Passengers */}
                      {result.passengers && renderPassengers(result.passengers)}
                      
                      {/* Boarding Passes */}
                      {result.boarding_passes && renderBoardingPasses(result.boarding_passes)}
                      
                      {/* Flight Segments */}
                      {result.segments && renderSegments(result.segments)}

                      {/* Data Sections */}
                      {result.passenger && renderSection('Passenger', result.passenger)}
                      {result.guest && renderSection('Guest', result.guest)}
                      {result.flight && renderSection('Flight Details', result.flight)}
                      {result.train && renderSection('Train Details', result.train)}
                      {result.hotel && renderSection('Hotel', result.hotel)}
                      {result.stay && renderSection('Stay Details', result.stay)}
                      {result.room && renderSection('Room', result.room)}
                      {result.boarding && renderSection('Boarding', result.boarding)}
                      {result.boarding_info && renderSection('Boarding Info', result.boarding_info)}
                      {result.seat && renderSection('Seat', result.seat)}
                      {result.booking && renderSection('Booking', result.booking)}
                      {result.fare && renderSection('Fare', result.fare)}
                      {result.rate && renderSection('Rate', result.rate)}
                      {result.payment && renderSection('Payment', result.payment)}
                      
                      {/* Cancellation Policy */}
                      {result.cancellation_policy && (
                        <div className="data-section">
                          <h4>Cancellation Policy</h4>
                          <p className="policy-text">{result.cancellation_policy}</p>
                        </div>
                      )}
                    </>
                  )}

                  {/* Documents Used */}
                  {result.documentsUsed && result.documentsUsed.length > 0 && (
                    <div className="documents-used">
                      <strong>Documents Used:</strong>
                      <div className="doc-tags">
                        {result.documentsUsed.map((doc, i) => (
                          <span key={i} className="doc-tag">{doc}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Download Button */}
                  <button
                    onClick={() => downloadJSON(result, `${docInfo.title.toLowerCase().replace(' ', '_')}_${index + 1}.json`)}
                    className="download-button"
                  >
                    <Download size={16} />
                    Download JSON
                  </button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ResultsPanel;

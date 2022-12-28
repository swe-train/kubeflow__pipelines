// Code generated by go-swagger; DO NOT EDIT.

package experiment_service

// This file was generated by the swagger tool.
// Editing this file might prove futile when you re-run the swagger generate command

import (
	"fmt"
	"io"

	"github.com/go-openapi/runtime"

	strfmt "github.com/go-openapi/strfmt"

	experiment_model "github.com/kubeflow/pipelines/backend/api/v2beta1/go_http_client/experiment_model"
)

// GetExperimentReader is a Reader for the GetExperiment structure.
type GetExperimentReader struct {
	formats strfmt.Registry
}

// ReadResponse reads a server response into the received o.
func (o *GetExperimentReader) ReadResponse(response runtime.ClientResponse, consumer runtime.Consumer) (interface{}, error) {
	switch response.Code() {

	case 200:
		result := NewGetExperimentOK()
		if err := result.readResponse(response, consumer, o.formats); err != nil {
			return nil, err
		}
		return result, nil

	default:
		return nil, runtime.NewAPIError("unknown error", response, response.Code())
	}
}

// NewGetExperimentOK creates a GetExperimentOK with default headers values
func NewGetExperimentOK() *GetExperimentOK {
	return &GetExperimentOK{}
}

/*GetExperimentOK handles this case with default header values.

A successful response.
*/
type GetExperimentOK struct {
	Payload *experiment_model.V2beta1Experiment
}

func (o *GetExperimentOK) Error() string {
	return fmt.Sprintf("[GET /apis/v2beta1/experiments/{experiment_id}][%d] getExperimentOK  %+v", 200, o.Payload)
}

func (o *GetExperimentOK) readResponse(response runtime.ClientResponse, consumer runtime.Consumer, formats strfmt.Registry) error {

	o.Payload = new(experiment_model.V2beta1Experiment)

	// response payload
	if err := consumer.Consume(response.Body(), o.Payload); err != nil && err != io.EOF {
		return err
	}

	return nil
}
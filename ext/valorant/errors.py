class ResponseError(Exception):
    '''
    Raised whenever an empty response is given by the Riot server.
    '''
    pass

class PhaseError(Exception):
    '''
    Raised whenever there's a problem while attempting to fetch phase data.
    This typically occurs when the phase is null (i.e. player is not in the agent select phase.)
    '''
    pass
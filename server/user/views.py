from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response


from .serializers import CustomerSerializer, UserSerializer

User = get_user_model()


class UserList(APIView):
    """
    An API View class for retrieving UserAccount list.

    Permissions
    -----------
        User must be an owner type

    Methods
    -------
    get(request)
        Handles a GET request to retrieve all users that aren't owners
    """

    def get(self, request, format=None):
        """
        Handles a GET request to retrieve all users that aren't owners
        """
        try:
            user = request.user

            if not user.is_superuser:
                return Response(
                    {'error': 'User doesn\'t have the proper '
                     'permissions for accessing customer data'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Only get users that aren't owners
            users = User.objects.order_by(
                '-date_created').filter(is_superuser=False)
            users = UserSerializer(users, many=True)

            return Response(
                {'users': users.data},
                status=status.HTTP_200_OK
            )

        except AttributeError:
            return Response(
                {'error': 'Something went wrong when retrieving customer data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CustomerList(APIView):
    """
    An API View class for retrieving Customer UserAccount list.

    Permissions
    -----------
        User must be an owner/Employee type

    Methods
    -------
    get(request)
        Handles a GET request to retrieve all Customers that aren't owners

        Optional Request Params:
            activated? : boolean
    """

    def get(self, request, format=None):
        """
        Handles a GET request to retrieve all Customers that aren't owners

        Optional Request Params:
            activated? : boolean
        """
        try:
            user = request.user

            activated = request.query_params.get('activated')

            if not (user.is_employee or user.is_superuser):
                return Response(
                    {'error': 'User doesn\'t have the proper permissions for accessing customer data'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # No 'activated' parameter
            if not activated:
                customers = User.objects.order_by(
                    '-date_created').filter(is_customer=True)
                customers = CustomerSerializer(customers, many=True)
                return Response(
                    {'customers': customers.data},
                    status=status.HTTP_200_OK
                )

            # Check if 'activated' parameter is available
            if activated == "true":
                customers = User.objects.order_by(
                    '-date_created').filter(is_customer=True, is_active=True)
                customers = CustomerSerializer(customers, many=True)

                return Response(
                    {'customers': customers.data},
                    status=status.HTTP_200_OK
                )

            if activated == "false":
                customers = User.objects.order_by(
                    '-date_created').filter(is_customer=True, is_active=False)
                customers = CustomerSerializer(customers, many=True)

                return Response(
                    {'customers': customers.data},
                    status=status.HTTP_200_OK
                )

            return Response(
                {'error': 'The \'activated\' parameter can only be true, false, or empty'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except AttributeError:
            return Response(
                {'error': 'Something went wrong when retrieving customer data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CustomerDetail(APIView):
    """
    An API View class for retrieving Customer UserAccount detail.

    Permissions
    -----------
        User must be an owner/Employee type

    Methods
    -------
    get(request)
        Handles a GET request to retrieve Customer detail
    """

    def get(self, request, id, format=None):
        """
        Handles a GET request to retrieve Customer detail
        """
        try:
            user = request.user

            if not (user.is_employee or user.is_superuser):
                return Response(
                    {'error': 'User doesn\'t have the proper permissions for accessing customer data'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            customer = User.objects.get(id=id)

            if customer.is_employee:
                return Response(
                    {'error': 'User is not a customer'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            customer = CustomerSerializer(customer, many=False)
            return Response(
                {'customer': customer.data},
                status=status.HTTP_200_OK
            )

        except ObjectDoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception:
            return Response(
                {'error': 'Something went wrong when retrieving customer data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BlacklistedUserList(APIView):
    """
    An API View class for retrieving blacklisted UserAccounts.

    Permissions
    -----------
        User must be an owner type

    Methods
    -------
    get(request)
        Handles a GET request to retrieve blacklisted UserAccounts detail
    """

    def get(self, request, format=None):
        """
        Handles a GET request to retrieve blacklisted UserAccounts detail
        """
        try:
            user = request.user

            if not user.is_superuser:
                return Response(
                    {'error': 'User doesn\'t have the proper permissions for accessing customer data'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            blacklisted_users = User.objects.order_by(
                '-date_created').filter(blacklisted=True)
            blacklisted_users = UserSerializer(blacklisted_users, many=True)

            return Response(
                {'blacklist': blacklisted_users.data},
                status=status.HTTP_200_OK
            )

        except AttributeError:
            return Response(
                {'error': 'Something went wrong when retrieving customer data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BlacklistUser(APIView):
    """
    An API View class for retrieving blacklisted UserAccounts.

    Permissions
    -----------
        User must be an owner type

    Methods
    -------
    patch(request)
        Handles a PATCH request to blacklist a user based on user_id
    """

    def patch(self, request, id, format=None):
        """
        Handles a PATCH request to blacklist a user based on user_id
        """
        try:
            user = request.user

            if not user.is_superuser:
                return Response(
                    {'error': 'User doesn\'t have the proper permissions'
                     ' for accessing customer data'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            user_to_blacklist = User.objects.get(id=id)

            if user_to_blacklist.is_superuser:
                return Response(
                    {'error': 'Cannot blacklist superusers'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user_to_blacklist.blacklisted:
                return Response(
                    {'error': 'User is already blacklisted'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            data = request.data
            if len(data) != 1 or not data['blacklisted'] or not data['memo']:
                return Response(
                    {'error': 'Body should only include \'blacklisted\' attribute'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = UserSerializer(
                user_to_blacklist, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'success': 'User has been blacklisted'},
                    status=status.HTTP_200_OK
                )

            return Response(
                {'error': 'Bad Request'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except KeyError:
            return Response(
                {'error': 'Something went wrong when retrieving customer data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except ObjectDoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception:
            return Response(
                {'error': 'Something went wrong when retrieving customer data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ActivateUser(APIView):
    """
    An API View class for activating Employee/Customer UserAccounts.

    Permissions
    -----------
        User must be an owner/Employee type

    Methods
    -------
    patch(request)
        Handles a PATCH request to activate a user
    """

    def patch(self, request, id, format=None):
        """
        Handles a PATCH request to activate a user
        """
        try:
            user = request.user

            user_to_activate = User.objects.get(id=id)

            if user_to_activate.is_active:
                return Response(
                    {'error': 'User is already activated'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if user_to_activate.is_employee and not user.is_superuser:
                return Response(
                    {'error': 'User doesn\'t have the proper permissions to activate employee users'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            data = request.data
            if len(data) != 2 or not data['is_active'] or not data['memo']:
                return Response(
                    {'error': 'Body should only include \'is_active\' attribute'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = UserSerializer(
                user_to_activate, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {'success': 'User has been activated'},
                    status=status.HTTP_200_OK
                )

            return Response(
                {'error': 'Bad Request'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except ObjectDoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        except KeyError:
            return Response(
                {'error': 'Necessary data was not passed properly'},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            return Response(
                {'error': 'Something went wrong when retrieving customer data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
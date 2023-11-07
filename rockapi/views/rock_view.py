from django.http import HttpResponseServerError
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rockapi.models import Rock, Type
from django.contrib.auth.models import User



class RockView(ViewSet):
    """Rock view set"""


    def create(self, request):
        """Handle POST requests for rocks

        Returns:
            Response: JSON serialized representation of newly created rock
        """

        # Get an object instance of a rock type
        chosen_type = Type.objects.get(pk=request.data['typeId'])

        # Create a rock object and assign it property values
        rock = Rock()
        rock.user = request.auth.user
        rock.weight = request.data['weight']
        rock.name = request.data['name']
        rock.type = chosen_type
        rock.save()

        serialized = RockSerializer(rock, many=False)

        return Response(serialized.data, status=status.HTTP_201_CREATED)
        

        # try:
        #     rock.save()
        #     serializer = RockSerializer(rock)
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # except Exception as ex:
        #     return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """Handle GET requests for single item

        Returns:
            Response -- JSON serialized instance
        """
        try:
            rock = Rock.objects.get(pk=pk)
            serializer = RockSerializer(rock)
            return Response(serializer.data)
        except Exception as ex:
            return Response({"reason": ex.args[0]}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Handle PUT requests

        Returns:
            Response -- Empty body with 204 status code
        """
        try:
            rock = Rock.objects.get(pk=pk)
            rock.sample_name = request.data["name"]
            rock.sample_description = request.data["description"]
            rock.save()
        except Rock.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return HttpResponseServerError(ex)

        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for a single item

        Returns:
            Response -- 200, 404, or 500 status code
        """
        try:
            rock = Rock.objects.get(pk=pk)

            # Verify that the pk of the rock owner is the same pk as the authenticated user
            if rock.user.id == request.auth.user.id:
                rock.delete()
                return Response(None, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'message': 'You do not own that rock'}, status=status.HTTP_403_FORBIDDEN)

        except Rock.DoesNotExist as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_404_NOT_FOUND)

        except Exception as ex:
            return Response({'message': ex.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request):
        """Handle GET requests for all items

        Returns:
            Response -- JSON serialized array
        """
        try:
            rocks = Rock.objects.all()
            serializer = RockSerializer(rocks, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as ex:
            return HttpResponseServerError(ex)


class RockTypeSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = Type
        fields = ( 'label', )

class RockOwnerSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    class Meta:
        model = User
        fields = ( 'first_name', 'last_name', )

class RockSerializer(serializers.ModelSerializer):
    """JSON serializer"""

    type = RockTypeSerializer(many=False)
    user = RockOwnerSerializer(many=False)

    class Meta:
        model = Rock
        fields = ( 'id', 'name', 'weight', 'user', 'type', )
